# -*- coding: utf-8 -*-

import json

from collections import Sequence
from datetime import datetime

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin  # NOQA

import cosm


DEFAULT_FORMAT = 'json'


class Client(object):

    api_version = 'v2'
    client_class = cosm.Client

    def __init__(self, key):
        self.client = self.client_class(key)
        self.client.base_url += '/{}/'.format(self.api_version)
        self.feeds = FeedsManager(self.client)


class ManagerBase(object):

    def _url(self, url_or_id):
        url = self.base_url
        if url_or_id:
            url += '/'
            url = urljoin(url, str(url_or_id))
        return url

    def _json_default(self, obj):
        if not isinstance(obj, datetime):
            raise TypeError
        return obj.isoformat() + 'Z'

    def _parse_datetime(self, value):
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")

    def _prepare_params(self, params):
        params = dict(params)
        for name, value in params.items():
            if isinstance(value, datetime):
                params[name] = value.isoformat() + 'Z'
        return params


class FeedsManager(ManagerBase):

    def __init__(self, client):
        self.client = client
        self.base_url = urljoin(client.base_url, 'feeds')

    def create(self, title, **kwargs):
        data = dict(title=title, **kwargs)
        response = self.client.post(self.base_url, data=data)
        response.raise_for_status()
        feed = cosm.Feed(**data)
        feed._manager = self
        feed._data['feed'] = response.headers['location']
        return feed

    def update(self, id_or_url, **kwargs):
        url = self._url(id_or_url)
        payload = json.dumps(kwargs)
        response = self.client.put(url, data=payload)
        response.raise_for_status()

    def list(self, **params):
        url = self._url(None)
        response = self.client.get(url, params=params)
        response.raise_for_status()
        json = response.json()
        for feed_data in json['results']:
            feed = cosm.Feed(**feed_data)
            feed._manager = self
            yield feed

    def get(self, url_or_id, **params):
        url = self._url(url_or_id)
        response = self.client.get(url, **params)
        response.raise_for_status()
        data = response.json()
        feed = cosm.Feed(**data)
        self._manager = self
        return feed

    def delete(self, url_or_id):
        url = self._url(url_or_id)
        response = self.client.delete(url)
        response.raise_for_status()


class DatastreamsManager(ManagerBase):

    def __init__(self, feed):
        self.feed = feed
        feed_manager = getattr(feed, '_manager', None)
        if feed_manager:
            self.client = feed_manager.client
            self.base_url = feed.feed + '/datastreams'
        else:
            self.client = None

    def create(self, id, **kwargs):
        data = dict(id=id, **kwargs)
        response = self.client.post(self.base_url, data=data)
        response.raise_for_status()
        datastream = cosm.Datastream(**data)
        datastream._manager = self
        return datastream

    def update(self, datastream_id, **kwargs):
        url = self._url(datastream_id)
        payload = json.dumps(kwargs)
        response = self.client.put(url, data=payload)
        response.raise_for_status()

    def list(self, **params):
        url = self._url('..')
        response = self.client.get(url, params=params)
        response.raise_for_status()
        json = response.json()
        for datastream_data in json['datastreams']:
            datastream = cosm.Datastream(**datastream_data)
            datastream._manager = self
            yield datastream

    def get(self, id, **params):
        url = self._url(id)
        params = self._prepare_params(params)
        response = self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        datapoints_data = data.pop('datapoints', None)
        datastream = cosm.Datastream(**data)
        datastream._manager = self
        if datapoints_data:
            datapoints = self._coerce_datapoints(
                datastream.datapoints, datapoints_data)
            datastream._data['datapoints'] = datapoints
        return datastream

    def delete(self, url_or_id):
        url = self._url(url_or_id)
        response = self.client.delete(url)
        response.raise_for_status()

    def _coerce_datapoints(self, datapoints_manager, datapoints_data):
        coerce = datapoints_manager._coerce_to_datapoint
        datapoints = []
        for data in datapoints_data:
            data['at'] = self._parse_datetime(data['at'])
            datapoint = coerce(data)
            datapoints.append(datapoint)
        return datapoints


class DatapointsManager(Sequence, ManagerBase):

    def __init__(self, datastream):
        self.datastream = datastream
        datastream_manager = getattr(datastream, '_manager', None)
        if datastream_manager:
            self.client = datastream._manager.client
            datastream_url = datastream._manager._url(datastream.id)
            self.base_url = datastream_url + '/datapoints'
        else:
            self.client = None

    def __contains__(self, value):
        return value in self.datapoints['datapoints']

    def __getitem__(self, item):
        return self._datapoints[item]

    def __len__(self):
        return len(self._datapoints)

    @property
    def _datapoints(self):
        return self.datastream._data['datapoints']

    def create(self, datapoints):
        datapoints = [self._coerce_to_datapoint(d) for d in datapoints]
        payload = json.dumps({
            'datapoints': [d.__getstate__() for d in datapoints],
        }, default=self._json_default)
        response = self.client.post(self.base_url, data=payload)
        response.raise_for_status()
        return datapoints

    def update(self, at, value):
        url = "{}/{}Z".format(self.base_url, at.isoformat())
        payload = json.dumps({'value': value})
        response = self.client.put(url, data=payload)
        response.raise_for_status()

    def get(self, at):
        url = "{}/{}Z".format(self.base_url, at.isoformat())
        response = self.client.get(url)
        response.raise_for_status()
        data = response.json()
        data['at'] = self._parse_datetime(data['at'])
        return self._coerce_to_datapoint(data)

    def history(self, **params):
        url = self._url('..').rstrip('/')
        params = self._prepare_params(params)
        response = self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        for datapoint_data in data['datapoints']:
            datapoint_data['at'] = self._parse_datetime(datapoint_data['at'])
            yield self._coerce_to_datapoint(datapoint_data)

    def delete(self, at=None, **params):
        url = self.base_url
        if at:
            url = "{}/{}Z".format(url, at.isoformat())
        elif params:
            params = self._prepare_params(params)
        response = self.client.delete(url, params=params)
        response.raise_for_status()

    def _coerce_to_datapoint(self, d):
        if isinstance(d, cosm.Datapoint):
            datapoint = self._clone_datapoint(d)
        elif isinstance(d, dict):
            datapoint = cosm.Datapoint(**d)
        datapoint._manager = self
        return datapoint

    def _clone_datapoint(self, d):
        return cosm.Datapoint(**d._data)
