#!/usr/bin/env python
# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for jmeter_cluster.py command line tool."""



import argparse
import os
import unittest

import apiclient
import apiclient.errors

import mock

from jmeter_cluster import JMeterCluster
from jmeter_cluster import JMeterExecuter


class JMeterClusterTest(unittest.TestCase):
  """Unit tests for JMeterCluster."""

  def setUp(self):
    self.mock_gce_api_constructor = mock.patch(
        'jmeter_cluster.GceApi').start()
    self.mock_gce_api = self.mock_gce_api_constructor.return_value
    self.mock_set_port_forward = mock.patch(
        'jmeter_cluster.JMeterCluster.SetPortForward').start()

  def tearDown(self):
    mock.patch.stopall()

  def testStart(self):
    self.mock_gce_api.GetInstance.return_value = {'status': 'RUNNING'}

    param = argparse.Namespace(size=3, prefix='foo')
    cluster = JMeterCluster(param)
    cluster.Start()

    self.assertEqual(1, self.mock_gce_api_constructor.call_count)
    self.assertEqual(3, self.mock_gce_api.CreateInstance.call_count)
    self.assertEqual('foo-000',
                      self.mock_gce_api.CreateInstance.call_args_list[0][0][0])
    self.assertEqual('foo-001',
                      self.mock_gce_api.CreateInstance.call_args_list[1][0][0])
    self.assertEqual('foo-002',
                      self.mock_gce_api.CreateInstance.call_args_list[2][0][0])
    self.assertEqual(3, self.mock_gce_api.GetInstance.call_count)

  def testShutdown(self):
    # Raising HttpError indicates the instance does not exist any more.
    self.mock_gce_api.GetInstance.side_effect = apiclient.errors.HttpError(
        '', '')
    # Make this list of list, so that the content can be overwritten from the
    # nested function.
    instance_list = [[
        {'name': 'bar-000'},
        {'name': 'bar-001'},
        {'name': 'bar-002'},
        {'name': 'bar-003'},
        {'name': 'bar-004'}]]
    def GetInstanceList(_):
      tmp = instance_list[0]
      instance_list[0] = []
      return tmp
    self.mock_gce_api.ListInstances.side_effect = GetInstanceList

    param = argparse.Namespace(prefix='bar')
    cluster = JMeterCluster(param)
    cluster.ShutDown()

    self.assertEqual(1, self.mock_gce_api_constructor.call_count)
    self.assertEqual(2, self.mock_gce_api.ListInstances.call_count)
    self.mock_gce_api.ListInstances.assert_called_with('name eq ^bar-.*')
    self.assertEqual(5, self.mock_gce_api.DeleteInstance.call_count)
    self.assertEqual('bar-000',
                      self.mock_gce_api.DeleteInstance.call_args_list[0][0][0])
    self.assertEqual('bar-001',
                      self.mock_gce_api.DeleteInstance.call_args_list[1][0][0])
    self.assertEqual('bar-002',
                      self.mock_gce_api.DeleteInstance.call_args_list[2][0][0])
    self.assertEqual('bar-003',
                      self.mock_gce_api.DeleteInstance.call_args_list[3][0][0])
    self.assertEqual('bar-004',
                      self.mock_gce_api.DeleteInstance.call_args_list[4][0][0])


class JMeterClusterExecuterTest(unittest.TestCase):
  """Unit tests for JMeterExecuter."""

  def setUp(self):
    self.mock_cluster_constructor = mock.patch(
        'jmeter_cluster.JMeterCluster').start()
    self.mock_cluster = self.mock_cluster_constructor.return_value
    self.mock_run_client = mock.patch(
        'jmeter_cluster.JMeterFiles.RunJmeterClient').start()

  def tearDown(self):
    mock.patch.stopall()

  def testStart(self):
    JMeterExecuter().ParseArgumentsAndExecute(['start'])

    self.assertEqual(1, self.mock_cluster_constructor.call_count)
    self.mock_cluster.Start.assert_called_once_with()
    param = self.mock_cluster_constructor.call_args_list[0][0][0]
    self.assertRegexpMatches(param.prefix, '^%s-jmeter' % os.environ['USER'])

  def testStartWithPrefix(self):
    JMeterExecuter().ParseArgumentsAndExecute(['start', '--prefix', 'abc'])

    self.assertEqual(1, self.mock_cluster_constructor.call_count)
    self.mock_cluster.Start.assert_called_once_with()
    param = self.mock_cluster_constructor.call_args_list[0][0][0]
    self.assertEqual('abc', param.prefix)

  def testStartWithSize(self):
    JMeterExecuter().ParseArgumentsAndExecute([
        'start', '10', '--prefix', 'abc', '--project', 'xyz'])

    self.assertEqual(1, self.mock_cluster_constructor.call_count)
    self.mock_cluster.Start.assert_called_once_with()
    param = self.mock_cluster_constructor.call_args_list[0][0][0]
    self.assertEqual('abc', param.prefix)
    self.assertEqual('xyz', param.project)
    self.assertEqual(10, param.size)

  def testClient(self):
    JMeterExecuter().ParseArgumentsAndExecute([
        'client'])

    self.mock_run_client.assert_called_once_with()

  def testClientWithParams(self):
    JMeterExecuter().ParseArgumentsAndExecute([
        'client', '--additional', 'parameters'])

    self.mock_run_client.assert_called_once_with('--additional', 'parameters')

  def testShutDown(self):
    JMeterExecuter().ParseArgumentsAndExecute(['shutdown'])

    self.assertEqual(1, self.mock_cluster_constructor.call_count)
    self.mock_cluster.ShutDown.assert_called_once_with()

  def testShutDownWithParams(self):
    JMeterExecuter().ParseArgumentsAndExecute([
        'shutdown', '--prefix', 'abc', '--project', 'xyz'])

    self.assertEqual(1, self.mock_cluster_constructor.call_count)
    self.mock_cluster.ShutDown.assert_called_once_with()
    param = self.mock_cluster_constructor.call_args_list[0][0][0]
    self.assertEqual('abc', param.prefix)
    self.assertEqual('xyz', param.project)


if __name__ == '__main__':
  unittest.main()
