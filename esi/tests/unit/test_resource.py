#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import itertools
import json
from unittest import mock

import requests

from esi import exceptions
from esi import format
from esi import resource
from esi.tests.unit import base
from esi import utils


class FakeResponse:
    def __init__(self, response, status_code=200, headers=None):
        self.body = response
        self.status_code = status_code
        headers = headers if headers else {'content-type': 'application/json'}
        self.headers = requests.structures.CaseInsensitiveDict(headers)

    def json(self):
        return self.body


class TestComponent(base.TestCase):
    class ExampleComponent(resource._BaseComponent):
        key = "_example"

    # Since we're testing ExampleComponent, which is as isolated as we
    # can test _BaseComponent due to it's needing to be a data member
    # of a class that has an attribute on the parent class named `key`,
    # each test has to implement a class with a name that is the same
    # as ExampleComponent.key, which should be a dict containing the
    # keys and values to test against.

    def test_implementations(self):
        self.assertEqual("_body", resource.Body.key)
        self.assertEqual("_header", resource.Header.key)
        self.assertEqual("_uri", resource.URI.key)

    def test_creation(self):
        sot = resource._BaseComponent(
            "name", type=int, default=1, alternate_id=True, aka="alias"
        )

        self.assertEqual("name", sot.name)
        self.assertEqual(int, sot.type)
        self.assertEqual(1, sot.default)
        self.assertEqual("alias", sot.aka)
        self.assertTrue(sot.alternate_id)

    def test_get_no_instance(self):
        sot = resource._BaseComponent("test")

        # Test that we short-circuit everything when given no instance.
        result = sot.__get__(None, None)
        self.assertIs(sot, result)

    # NOTE: Some tests will use a default=1 setting when testing result
    # values that should be None because the default-for-default is also None.
    def test_get_name_None(self):
        name = "name"

        class Parent:
            _example = {name: None}

        instance = Parent()
        sot = TestComponent.ExampleComponent(name, default=1)

        # Test that we short-circuit any typing of a None value.
        result = sot.__get__(instance, None)
        self.assertIsNone(result)

    def test_get_default(self):
        expected_result = 123

        class Parent:
            _example = {}

        instance = Parent()
        # NOTE: type=dict but the default value is an int. If we didn't
        # short-circuit the typing part of __get__ it would fail.
        sot = TestComponent.ExampleComponent(
            "name", type=dict, default=expected_result
        )

        # Test that we directly return any default value.
        result = sot.__get__(instance, None)
        self.assertEqual(expected_result, result)

    def test_get_name_untyped(self):
        name = "name"
        expected_result = 123

        class Parent:
            _example = {name: expected_result}

        instance = Parent()
        sot = TestComponent.ExampleComponent("name")

        # Test that we return any the value as it is set.
        result = sot.__get__(instance, None)
        self.assertEqual(expected_result, result)

    # The code path for typing after a raw value has been found is the same.
    def test_get_name_typed(self):
        name = "name"
        value = "123"

        class Parent:
            _example = {name: value}

        instance = Parent()
        sot = TestComponent.ExampleComponent("name", type=int)

        # Test that we run the underlying value through type conversion.
        result = sot.__get__(instance, None)
        self.assertEqual(int(value), result)

    def test_get_name_formatter(self):
        name = "name"
        value = "123"
        expected_result = "one hundred twenty three"

        class Parent:
            _example = {name: value}

        class FakeFormatter(format.Formatter):
            @classmethod
            def deserialize(cls, value):
                return expected_result

        instance = Parent()
        sot = TestComponent.ExampleComponent("name", type=FakeFormatter)

        # Mock out issubclass rather than having an actual format.Formatter
        # This can't be mocked via decorator, isolate it to wrapping the call.
        result = sot.__get__(instance, None)
        self.assertEqual(expected_result, result)

    def test_set_name_untyped(self):
        name = "name"
        expected_value = "123"

        class Parent:
            _example = {}

        instance = Parent()
        sot = TestComponent.ExampleComponent("name")

        # Test that we don't run the value through type conversion.
        sot.__set__(instance, expected_value)
        self.assertEqual(expected_value, instance._example[name])

    def test_set_name_typed(self):
        expected_value = "123"

        class Parent:
            _example = {}

        instance = Parent()

        # The type we give to ExampleComponent has to be an actual type,
        # not an instance, so we can't get the niceties of a mock.Mock
        # instance that would allow us to call `assert_called_once_with` to
        # ensure that we're sending the value through the type.
        # Instead, we use this tiny version of a similar thing.
        class FakeType:
            calls = []

            def __init__(self, arg):
                FakeType.calls.append(arg)

        sot = TestComponent.ExampleComponent("name", type=FakeType)

        # Test that we run the value through type conversion.
        sot.__set__(instance, expected_value)
        self.assertEqual([expected_value], FakeType.calls)

    def test_set_name_formatter(self):
        expected_value = "123"

        class Parent:
            _example = {}

        instance = Parent()

        # As with test_set_name_typed, create a pseudo-Mock to track what
        # gets called on the type.
        class FakeFormatter(format.Formatter):
            calls = []

            @classmethod
            def serialize(cls, arg):
                FakeFormatter.calls.append(arg)

            @classmethod
            def deserialize(cls, arg):
                FakeFormatter.calls.append(arg)

        sot = TestComponent.ExampleComponent("name", type=FakeFormatter)

        # Test that we run the value through type conversion.
        sot.__set__(instance, expected_value)
        self.assertEqual([expected_value], FakeFormatter.calls)

    def test_delete_name(self):
        name = "name"
        expected_value = "123"

        class Parent:
            _example = {name: expected_value}

        instance = Parent()

        sot = TestComponent.ExampleComponent("name")

        sot.__delete__(instance)

        self.assertNotIn(name, instance._example)

    def test_delete_name_doesnt_exist(self):
        name = "name"
        expected_value = "123"

        class Parent:
            _example = {"what": expected_value}

        instance = Parent()

        sot = TestComponent.ExampleComponent(name)

        sot.__delete__(instance)

        self.assertNotIn(name, instance._example)


class TestComponentManager(base.TestCase):
    def test_create_basic(self):
        sot = resource._ComponentManager()
        self.assertEqual(dict(), sot.attributes)
        self.assertEqual(set(), sot._dirty)

    def test_create_unsynced(self):
        attrs = {"hey": 1, "hi": 2, "hello": 3}
        sync = False

        sot = resource._ComponentManager(attributes=attrs, synchronized=sync)
        self.assertEqual(attrs, sot.attributes)
        self.assertEqual(set(attrs.keys()), sot._dirty)

    def test_create_synced(self):
        attrs = {"hey": 1, "hi": 2, "hello": 3}
        sync = True

        sot = resource._ComponentManager(attributes=attrs, synchronized=sync)
        self.assertEqual(attrs, sot.attributes)
        self.assertEqual(set(), sot._dirty)

    def test_getitem(self):
        key = "key"
        value = "value"
        attrs = {key: value}

        sot = resource._ComponentManager(attributes=attrs)
        self.assertEqual(value, sot.__getitem__(key))

    def test_setitem_new(self):
        key = "key"
        value = "value"

        sot = resource._ComponentManager()
        sot.__setitem__(key, value)

        self.assertIn(key, sot.attributes)
        self.assertIn(key, sot.dirty)

    def test_setitem_unchanged(self):
        key = "key"
        value = "value"
        attrs = {key: value}

        sot = resource._ComponentManager(attributes=attrs, synchronized=True)
        # This shouldn't end up in the dirty list since we're just re-setting.
        sot.__setitem__(key, value)

        self.assertEqual(value, sot.attributes[key])
        self.assertNotIn(key, sot.dirty)

    def test_delitem(self):
        key = "key"
        value = "value"
        attrs = {key: value}

        sot = resource._ComponentManager(attributes=attrs, synchronized=True)
        sot.__delitem__(key)

        self.assertIsNone(sot.dirty[key])

    def test_iter(self):
        attrs = {"key": "value"}
        sot = resource._ComponentManager(attributes=attrs)
        self.assertCountEqual(iter(attrs), sot.__iter__())

    def test_len(self):
        attrs = {"key": "value"}
        sot = resource._ComponentManager(attributes=attrs)
        self.assertEqual(len(attrs), sot.__len__())

    def test_dirty(self):
        key = "key"
        key2 = "key2"
        value = "value"
        attrs = {key: value}
        sot = resource._ComponentManager(attributes=attrs, synchronized=False)
        self.assertEqual({key: value}, sot.dirty)

        sot.__setitem__(key2, value)
        self.assertEqual({key: value, key2: value}, sot.dirty)

    def test_clean(self):
        key = "key"
        value = "value"
        attrs = {key: value}
        sot = resource._ComponentManager(attributes=attrs, synchronized=False)
        self.assertEqual(attrs, sot.dirty)

        sot.clean()

        self.assertEqual(dict(), sot.dirty)


class Test_Request(base.TestCase):
    def test_create(self):
        uri = 1
        body = 2
        headers = 3

        sot = resource._Request(uri, body, headers)

        self.assertEqual(uri, sot.url)
        self.assertEqual(body, sot.body)
        self.assertEqual(headers, sot.headers)


class TestQueryParameters(base.TestCase):
    def test_create(self):
        location = "location"
        mapping = {
            "first_name": "first-name",
            "second_name": {"name": "second-name"},
            "third_name": {"name": "third", "type": int},
        }

        sot = resource.QueryParameters(location, **mapping)

        self.assertEqual(
            {
                "location": "location",
                "first_name": "first-name",
                "second_name": {"name": "second-name"},
                "third_name": {"name": "third", "type": int},
                "limit": "limit",
                "marker": "marker",
            },
            sot._mapping,
        )

    def test_transpose_unmapped(self):
        def _type(value, rtype):
            self.assertIs(rtype, mock.sentinel.resource_type)
            return value * 10

        location = "location"
        mapping = {
            "first_name": "first-name",
            "pet_name": {"name": "pet"},
            "answer": {"name": "answer", "type": int},
            "complex": {"type": _type},
        }

        sot = resource.QueryParameters(location, **mapping)
        result = sot._transpose(
            {
                "location": "Brooklyn",
                "first_name": "Brian",
                "pet_name": "Meow",
                "answer": "42",
                "last_name": "Curtin",
                "complex": 1,
            },
            mock.sentinel.resource_type,
        )

        # last_name isn't mapped and shouldn't be included
        self.assertEqual(
            {
                "location": "Brooklyn",
                "first-name": "Brian",
                "pet": "Meow",
                "answer": 42,
                "complex": 10,
            },
            result,
        )

    def test_transpose_not_in_query(self):
        location = "location"
        mapping = {
            "first_name": "first-name",
            "pet_name": {"name": "pet"},
            "answer": {"name": "answer", "type": int},
        }

        sot = resource.QueryParameters(location, **mapping)
        result = sot._transpose(
            {"location": "Brooklyn"}, mock.sentinel.resource_type
        )

        # first_name not being in the query shouldn't affect results
        self.assertEqual({"location": "Brooklyn"}, result)


class TestResource(base.TestCase):
    def test_initialize_basic(self):
        body = {"body": 1}
        header = {"header": 2, "Location": "somewhere"}
        uri = {"uri": 3}
        computed = {"computed": 4}
        everything = dict(
            itertools.chain(
                body.items(),
                header.items(),
                uri.items(),
                computed.items(),
            )
        )

        mock_collect = mock.Mock()
        mock_collect.return_value = body, header, uri, computed

        with mock.patch.object(
            resource.Resource, "_collect_attrs", mock_collect
        ):
            sot = resource.Resource(_synchronized=False, **everything)
            mock_collect.assert_called_once_with(everything)
        self.assertIsNone(sot.location)

        self.assertIsInstance(sot._body, resource._ComponentManager)
        self.assertEqual(body, sot._body.dirty)
        self.assertIsInstance(sot._header, resource._ComponentManager)
        self.assertEqual(header, sot._header.dirty)
        self.assertIsInstance(sot._uri, resource._ComponentManager)
        self.assertEqual(uri, sot._uri.dirty)

        self.assertFalse(sot.allow_create)
        self.assertFalse(sot.allow_fetch)
        self.assertFalse(sot.allow_commit)
        self.assertFalse(sot.allow_delete)
        self.assertFalse(sot.allow_list)
        self.assertFalse(sot.allow_head)
        self.assertEqual('PUT', sot.commit_method)
        self.assertEqual('POST', sot.create_method)

    def test_repr(self):
        a = {"a": 1}
        b = {"b": 2}
        c = {"c": 3}
        d = {"d": 4}

        class Test(resource.Resource):
            def __init__(self):
                self._body = mock.Mock()
                self._body.attributes.items = mock.Mock(return_value=a.items())

                self._header = mock.Mock()
                self._header.attributes.items = mock.Mock(
                    return_value=b.items()
                )

                self._uri = mock.Mock()
                self._uri.attributes.items = mock.Mock(return_value=c.items())

                self._computed = mock.Mock()
                self._computed.attributes.items = mock.Mock(
                    return_value=d.items()
                )

        the_repr = repr(Test())

        # Don't test the arguments all together since the dictionary order
        # they're rendered in can't be depended on, nor does it matter.
        self.assertIn("esi.tests.unit.test_resource.Test", the_repr)
        self.assertIn("a=1", the_repr)
        self.assertIn("b=2", the_repr)
        self.assertIn("c=3", the_repr)
        self.assertIn("d=4", the_repr)

    def test_equality(self):
        class Example(resource.Resource):
            x = resource.Body("x")
            y = resource.Header("y")
            z = resource.URI("z")

        e1 = Example(x=1, y=2, z=3)
        e2 = Example(x=1, y=2, z=3)
        e3 = Example(x=0, y=0, z=0)

        self.assertEqual(e1, e2)
        self.assertNotEqual(e1, e3)
        self.assertNotEqual(e1, None)

    def test__update(self):
        sot = resource.Resource()

        body = "body"
        header = "header"
        uri = "uri"
        computed = "computed"

        sot._collect_attrs = mock.Mock(
            return_value=(body, header, uri, computed)
        )
        sot._body.update = mock.Mock()
        sot._header.update = mock.Mock()
        sot._uri.update = mock.Mock()
        sot._computed.update = mock.Mock()

        args = {"arg": 1}
        sot._update(**args)

        sot._collect_attrs.assert_called_once_with(args)
        sot._body.update.assert_called_once_with(body)
        sot._header.update.assert_called_once_with(header)
        sot._uri.update.assert_called_once_with(uri)
        sot._computed.update.assert_called_with(computed)

    def test__consume_attrs(self):
        serverside_key1 = "someKey1"
        clientside_key1 = "some_key1"
        serverside_key2 = "someKey2"
        clientside_key2 = "some_key2"
        value1 = "value1"
        value2 = "value2"
        mapping = {
            serverside_key1: clientside_key1,
            serverside_key2: clientside_key2,
        }

        other_key = "otherKey"
        other_value = "other"
        attrs = {
            clientside_key1: value1,
            serverside_key2: value2,
            other_key: other_value,
        }

        sot = resource.Resource()

        result = sot._consume_attrs(mapping, attrs)

        # Make sure that the expected key was consumed and we're only
        # left with the other stuff.
        self.assertDictEqual({other_key: other_value}, attrs)

        # Make sure that after we've popped our relevant client-side
        # key off that we are returning it keyed off of its server-side
        # name.
        self.assertDictEqual(
            {serverside_key1: value1, serverside_key2: value2}, result
        )

    def test__mapping_defaults(self):
        # Check that even on an empty class, we get the expected
        # built-in attributes.

        self.assertIn("location", resource.Resource._computed_mapping())
        self.assertIn("name", resource.Resource._body_mapping())
        self.assertIn("id", resource.Resource._body_mapping())

    def test__mapping_overrides(self):
        # Iterating through the MRO used to wipe out overrides of mappings
        # found in base classes.
        new_name = "MyName"
        new_id = "MyID"

        class Test(resource.Resource):
            name = resource.Body(new_name)
            id = resource.Body(new_id)

        mapping = Test._body_mapping()

        self.assertEqual("name", mapping["MyName"])
        self.assertEqual("id", mapping["MyID"])

    def test__body_mapping(self):
        class Test(resource.Resource):
            x = resource.Body("x")
            y = resource.Body("y")
            z = resource.Body("z")

        self.assertIn("x", Test._body_mapping())
        self.assertIn("y", Test._body_mapping())
        self.assertIn("z", Test._body_mapping())

    def test__header_mapping(self):
        class Test(resource.Resource):
            x = resource.Header("x")
            y = resource.Header("y")
            z = resource.Header("z")

        self.assertIn("x", Test._header_mapping())
        self.assertIn("y", Test._header_mapping())
        self.assertIn("z", Test._header_mapping())

    def test__uri_mapping(self):
        class Test(resource.Resource):
            x = resource.URI("x")
            y = resource.URI("y")
            z = resource.URI("z")

        self.assertIn("x", Test._uri_mapping())
        self.assertIn("y", Test._uri_mapping())
        self.assertIn("z", Test._uri_mapping())

    def test__getattribute__id_in_body(self):
        id = "lol"
        sot = resource.Resource(id=id)

        result = getattr(sot, "id")
        self.assertEqual(result, id)

    def test__getattribute__id_with_alternate(self):
        id = "lol"

        class Test(resource.Resource):
            blah = resource.Body("blah", alternate_id=True)

        sot = Test(blah=id)

        result = getattr(sot, "id")
        self.assertEqual(result, id)

    def test__getattribute__id_without_alternate(self):
        class Test(resource.Resource):
            id = None

        sot = Test()
        self.assertIsNone(sot.id)

    def test__alternate_id_None(self):
        self.assertEqual("", resource.Resource._alternate_id())

    def test__alternate_id(self):
        class Test(resource.Resource):
            alt = resource.Body("the_alt", alternate_id=True)

        self.assertEqual("the_alt", Test._alternate_id())

        value1 = "lol"
        sot = Test(alt=value1)
        self.assertEqual(sot.alt, value1)
        self.assertEqual(sot.id, value1)

        value2 = "rofl"
        sot = Test(the_alt=value2)
        self.assertEqual(sot.alt, value2)
        self.assertEqual(sot.id, value2)

    def test__alternate_id_from_other_property(self):
        class Test(resource.Resource):
            foo = resource.Body("foo")
            bar = resource.Body("bar", alternate_id=True)

        # NOTE(redrobot): My expectation looking at the Test class defined
        # in this test is that because the alternate_id parameter is
        # is being set to True on the "bar" property of the Test class,
        # then the _alternate_id() method should return the name of that "bar"
        # property.
        self.assertEqual("bar", Test._alternate_id())
        sot = Test(bar='bunnies')
        self.assertEqual(sot.id, 'bunnies')
        self.assertEqual(sot.bar, 'bunnies')
        sot = Test(id='chickens', bar='bunnies')
        self.assertEqual(sot.id, 'chickens')
        self.assertEqual(sot.bar, 'bunnies')

    def test__get_id_instance(self):
        class Test(resource.Resource):
            id = resource.Body("id")

        value = "id"
        sot = Test(id=value)

        self.assertEqual(value, sot._get_id(sot))

    def test__get_id_instance_alternate(self):
        class Test(resource.Resource):
            attr = resource.Body("attr", alternate_id=True)

        value = "id"
        sot = Test(attr=value)

        self.assertEqual(value, sot._get_id(sot))

    def test__get_id_value(self):
        value = "id"
        self.assertEqual(value, resource.Resource._get_id(value))

    def test__attributes(self):
        class Test(resource.Resource):
            foo = resource.Header('foo')
            bar = resource.Body('bar', aka='_bar')
            bar_local = resource.Body('bar_remote')

        sot = Test()

        self.assertEqual(
            sorted(
                ['foo', 'bar', '_bar', 'bar_local', 'id', 'name', 'location']
            ),
            sorted(sot._attributes()),
        )

        self.assertEqual(
            sorted(['foo', 'bar', 'bar_local', 'id', 'name', 'location']),
            sorted(sot._attributes(include_aliases=False)),
        )

        self.assertEqual(
            sorted(
                ['foo', 'bar', '_bar', 'bar_remote', 'id', 'name', 'location']
            ),
            sorted(sot._attributes(remote_names=True)),
        )

        self.assertEqual(
            sorted(['bar', '_bar', 'bar_local', 'id', 'name', 'location']),
            sorted(
                sot._attributes(
                    components=tuple([resource.Body, resource.Computed])
                )
            ),
        )

        self.assertEqual(
            ('foo',),
            tuple(sot._attributes(components=tuple([resource.Header]))),
        )

    def test__attributes_iterator(self):
        class Parent(resource.Resource):
            foo = resource.Header('foo')
            bar = resource.Body('bar', aka='_bar')

        class Child(Parent):
            foo1 = resource.Header('foo1')
            bar1 = resource.Body('bar1')

        sot = Child()
        expected = ['foo', 'bar', 'foo1', 'bar1']

        for attr, component in sot._attributes_iterator():
            if attr in expected:
                expected.remove(attr)
        self.assertEqual([], expected)

        expected = ['foo', 'foo1']

        # Check we iterate only over headers
        for attr, component in sot._attributes_iterator(
            components=tuple([resource.Header])
        ):
            if attr in expected:
                expected.remove(attr)
        self.assertEqual([], expected)

    def test_to_dict(self):
        class Test(resource.Resource):
            foo = resource.Header('foo')
            bar = resource.Body('bar', aka='_bar')

        res = Test(id='FAKE_ID')

        expected = {
            'id': 'FAKE_ID',
            'name': None,
            'location': None,
            'foo': None,
            'bar': None,
            '_bar': None,
        }
        self.assertEqual(expected, res.to_dict())

    def test_to_dict_nested(self):
        class Test(resource.Resource):
            foo = resource.Header('foo')
            bar = resource.Body('bar')
            a_list = resource.Body('a_list')

        class Sub(resource.Resource):
            sub = resource.Body('foo')

        sub = Sub(id='ANOTHER_ID', foo='bar')

        res = Test(id='FAKE_ID', bar=sub, a_list=[sub])

        expected = {
            'id': 'FAKE_ID',
            'name': None,
            'location': None,
            'foo': None,
            'bar': {
                'id': 'ANOTHER_ID',
                'name': None,
                'sub': 'bar',
                'location': None,
            },
            'a_list': [
                {
                    'id': 'ANOTHER_ID',
                    'name': None,
                    'sub': 'bar',
                    'location': None,
                }
            ],
        }
        self.assertEqual(expected, res.to_dict())
        a_munch = res.to_dict(_to_munch=True)
        self.assertEqual(a_munch.bar.id, 'ANOTHER_ID')
        self.assertEqual(a_munch.bar.sub, 'bar')
        self.assertEqual(a_munch.a_list[0].id, 'ANOTHER_ID')
        self.assertEqual(a_munch.a_list[0].sub, 'bar')

    def test_to_dict_no_body(self):
        class Test(resource.Resource):
            foo = resource.Header('foo')
            bar = resource.Body('bar')

        res = Test(id='FAKE_ID')

        expected = {
            'location': None,
            'foo': None,
        }
        self.assertEqual(expected, res.to_dict(body=False))

    def test_to_dict_no_header(self):
        class Test(resource.Resource):
            foo = resource.Header('foo')
            bar = resource.Body('bar')

        res = Test(id='FAKE_ID')

        expected = {
            'id': 'FAKE_ID',
            'name': None,
            'bar': None,
            'location': None,
        }
        self.assertEqual(expected, res.to_dict(headers=False))

    def test_to_dict_ignore_none(self):
        class Test(resource.Resource):
            foo = resource.Header('foo')
            bar = resource.Body('bar')

        res = Test(id='FAKE_ID', bar='BAR')

        expected = {
            'id': 'FAKE_ID',
            'bar': 'BAR',
        }
        self.assertEqual(expected, res.to_dict(ignore_none=True))

    def test_to_dict_with_mro(self):
        class Parent(resource.Resource):
            foo = resource.Header('foo')
            bar = resource.Body('bar', aka='_bar')

        class Child(Parent):
            foo_new = resource.Header('foo_baz_server')
            bar_new = resource.Body('bar_baz_server')

        res = Child(id='FAKE_ID', bar='test')

        expected = {
            'foo': None,
            'bar': 'test',
            '_bar': 'test',
            'foo_new': None,
            'bar_new': None,
            'id': 'FAKE_ID',
            'location': None,
            'name': None,
        }
        self.assertEqual(expected, res.to_dict())

    def test_to_dict_with_unknown_attrs_in_body(self):
        class Test(resource.Resource):
            foo = resource.Body('foo')
            _allow_unknown_attrs_in_body = True

        res = Test(id='FAKE_ID', foo='FOO', bar='BAR')

        expected = {
            'id': 'FAKE_ID',
            'name': None,
            'location': None,
            'foo': 'FOO',
            'bar': 'BAR',
        }
        self.assertEqual(expected, res.to_dict())

    def test_json_dumps_from_resource(self):
        class Test(resource.Resource):
            foo = resource.Body('foo_remote')

        res = Test(foo='bar')

        expected = '{"foo": "bar", "id": null, "location": null, "name": null}'

        actual = json.dumps(res, sort_keys=True)
        self.assertEqual(expected, actual)

        response = FakeResponse({'foo': 'new_bar'})
        res._translate_response(response)

        expected = (
            '{"foo": "new_bar", "id": null, "location": null, "name": null}'
        )
        actual = json.dumps(res, sort_keys=True)
        self.assertEqual(expected, actual)

    def test_items(self):
        class Test(resource.Resource):
            foo = resource.Body('foo')
            bar = resource.Body('bar')
            foot = resource.Body('foot')

        data = {'foo': 'bar', 'bar': 'foo\n', 'foot': 'a:b:c:d'}

        res = Test(**data)
        for k, v in res.items():
            expected = data.get(k)
            if expected:
                self.assertEqual(v, expected)

    def test_access_by_aka(self):
        class Test(resource.Resource):
            foo = resource.Header('foo_remote', aka='foo_alias')

        res = Test(foo='bar', name='test')

        self.assertEqual('bar', res['foo_alias'])
        self.assertEqual('bar', res.foo_alias)
        self.assertTrue('foo' in res.keys())
        self.assertTrue('foo_alias' in res.keys())
        expected = utils.Munch(
            {
                'id': None,
                'name': 'test',
                'location': None,
                'foo': 'bar',
                'foo_alias': 'bar',
            }
        )
        actual = utils.Munch(res)
        self.assertEqual(expected, actual)
        self.assertEqual(expected, res.toDict())
        self.assertEqual(expected, res.to_dict())
        self.assertDictEqual(expected, res)
        self.assertDictEqual(expected, dict(res))

    def test_access_by_resource_name(self):
        class Test(resource.Resource):
            blah = resource.Body("blah_resource")

        sot = Test(blah='dummy')

        result = sot["blah_resource"]
        self.assertEqual(result, sot.blah)

    def test_to_dict_value_error(self):
        class Test(resource.Resource):
            foo = resource.Header('foo')
            bar = resource.Body('bar')

        res = Test(id='FAKE_ID')

        err = self.assertRaises(
            ValueError, res.to_dict, body=False, headers=False, computed=False
        )
        self.assertEqual(
            'At least one of `body`, `headers` or `computed` must be True',
            str(err),
        )

    def test_to_dict_with_mro_no_override(self):
        class Parent(resource.Resource):
            header = resource.Header('HEADER')
            body = resource.Body('BODY')

        class Child(Parent):
            # The following two properties are not supposed to be overridden
            # by the parent class property values.
            header = resource.Header('ANOTHER_HEADER')
            body = resource.Body('ANOTHER_BODY')

        res = Child(id='FAKE_ID', body='BODY_VALUE', header='HEADER_VALUE')

        expected = {
            'body': 'BODY_VALUE',
            'header': 'HEADER_VALUE',
            'id': 'FAKE_ID',
            'location': None,
            'name': None,
        }
        self.assertEqual(expected, res.to_dict())

    def test_new(self):
        class Test(resource.Resource):
            attr = resource.Body("attr")

        value = "value"
        sot = Test.new(attr=value)

        self.assertIn("attr", sot._body.dirty)
        self.assertEqual(value, sot.attr)

    def test_existing(self):
        class Test(resource.Resource):
            attr = resource.Body("attr")

        value = "value"
        sot = Test.existing(attr=value)

        self.assertNotIn("attr", sot._body.dirty)
        self.assertEqual(value, sot.attr)

    def test_from_munch_new(self):
        class Test(resource.Resource):
            attr = resource.Body("body_attr")

        value = "value"
        orig = utils.Munch(body_attr=value)
        sot = Test._from_munch(orig, synchronized=False)

        self.assertIn("body_attr", sot._body.dirty)
        self.assertEqual(value, sot.attr)

    def test_from_munch_existing(self):
        class Test(resource.Resource):
            attr = resource.Body("body_attr")

        value = "value"
        orig = utils.Munch(body_attr=value)
        sot = Test._from_munch(orig)

        self.assertNotIn("body_attr", sot._body.dirty)
        self.assertEqual(value, sot.attr)

    def test__prepare_request_with_id(self):
        class Test(resource.Resource):
            base_path = "/something"
            body_attr = resource.Body("x")
            header_attr = resource.Header("y")

        the_id = "id"
        body_value = "body"
        header_value = "header"
        sot = Test(
            id=the_id,
            body_attr=body_value,
            header_attr=header_value,
            _synchronized=False,
        )

        result = sot._prepare_request(requires_id=True)

        self.assertEqual("something/id", result.url)
        self.assertEqual({"x": body_value, "id": the_id}, result.body)
        self.assertEqual({"y": header_value}, result.headers)

    def test__prepare_request_with_id_marked_clean(self):
        class Test(resource.Resource):
            base_path = "/something"
            body_attr = resource.Body("x")
            header_attr = resource.Header("y")

        the_id = "id"
        body_value = "body"
        header_value = "header"
        sot = Test(
            id=the_id,
            body_attr=body_value,
            header_attr=header_value,
            _synchronized=False,
        )
        sot._body._dirty.discard("id")

        result = sot._prepare_request(requires_id=True)

        self.assertEqual("something/id", result.url)
        self.assertEqual({"x": body_value}, result.body)
        self.assertEqual({"y": header_value}, result.headers)

    def test__prepare_request_missing_id(self):
        sot = resource.Resource(id=None)

        self.assertRaises(
            exceptions.InvalidRequest, sot._prepare_request, requires_id=True
        )

    def test__prepare_request_with_resource_key(self):
        key = "key"

        class Test(resource.Resource):
            base_path = "/something"
            resource_key = key
            body_attr = resource.Body("x")
            header_attr = resource.Header("y")

        body_value = "body"
        header_value = "header"
        sot = Test(
            body_attr=body_value, header_attr=header_value, _synchronized=False
        )

        result = sot._prepare_request(requires_id=False, prepend_key=True)

        self.assertEqual("/something", result.url)
        self.assertEqual({key: {"x": body_value}}, result.body)
        self.assertEqual({"y": header_value}, result.headers)

    def test__prepare_request_with_override_key(self):
        default_key = "key"
        override_key = "other_key"

        class Test(resource.Resource):
            base_path = "/something"
            resource_key = default_key
            body_attr = resource.Body("x")
            header_attr = resource.Header("y")

        body_value = "body"
        header_value = "header"
        sot = Test(
            body_attr=body_value, header_attr=header_value, _synchronized=False
        )

        result = sot._prepare_request(
            requires_id=False,
            prepend_key=True,
            resource_request_key=override_key,
        )

        self.assertEqual("/something", result.url)
        self.assertEqual({override_key: {"x": body_value}}, result.body)
        self.assertEqual({"y": header_value}, result.headers)

    def test__prepare_request_with_patch(self):
        class Test(resource.Resource):
            commit_jsonpatch = True
            base_path = "/something"
            x = resource.Body("x")
            y = resource.Body("y")

        the_id = "id"
        sot = Test.existing(id=the_id, x=1, y=2)
        sot.x = 3

        result = sot._prepare_request(requires_id=True, patch=True)

        self.assertEqual("something/id", result.url)
        self.assertEqual(
            [{'op': 'replace', 'path': '/x', 'value': 3}], result.body
        )

    def test__prepare_request_with_patch_not_synchronized(self):
        class Test(resource.Resource):
            commit_jsonpatch = True
            base_path = "/something"
            x = resource.Body("x")
            y = resource.Body("y")

        the_id = "id"
        sot = Test.new(id=the_id, x=1)

        result = sot._prepare_request(requires_id=True, patch=True)

        self.assertEqual("something/id", result.url)
        self.assertEqual(
            [{'op': 'add', 'path': '/x', 'value': 1}], result.body
        )

    def test__prepare_request_with_patch_params(self):
        class Test(resource.Resource):
            commit_jsonpatch = True
            base_path = "/something"
            x = resource.Body("x")
            y = resource.Body("y")

        the_id = "id"
        sot = Test.existing(id=the_id, x=1, y=2)
        sot.x = 3

        params = [('foo', 'bar'), ('life', 42)]

        result = sot._prepare_request(
            requires_id=True, patch=True, params=params
        )

        self.assertEqual("something/id?foo=bar&life=42", result.url)
        self.assertEqual(
            [{'op': 'replace', 'path': '/x', 'value': 3}], result.body
        )

    def test__translate_response_no_body(self):
        class Test(resource.Resource):
            attr = resource.Header("attr")

        response = FakeResponse({}, headers={"attr": "value"})

        sot = Test()

        sot._translate_response(response, has_body=False)

        self.assertEqual(dict(), sot._header.dirty)
        self.assertEqual("value", sot.attr)

    def test__translate_response_with_body_no_resource_key(self):
        class Test(resource.Resource):
            attr = resource.Body("attr")

        body = {"attr": "value"}
        response = FakeResponse(body)

        sot = Test()
        sot._filter_component = mock.Mock(side_effect=[body, dict()])

        sot._translate_response(response, has_body=True)

        self.assertEqual("value", sot.attr)
        self.assertEqual(dict(), sot._body.dirty)
        self.assertEqual(dict(), sot._header.dirty)

    def test__translate_response_with_body_with_resource_key(self):
        key = "key"

        class Test(resource.Resource):
            resource_key = key
            attr = resource.Body("attr")

        body = {"attr": "value"}
        response = FakeResponse({key: body})

        sot = Test()
        sot._filter_component = mock.Mock(side_effect=[body, dict()])

        sot._translate_response(response, has_body=True)

        self.assertEqual("value", sot.attr)
        self.assertEqual(dict(), sot._body.dirty)
        self.assertEqual(dict(), sot._header.dirty)

    def test_cant_do_anything(self):
        class Test(resource.Resource):
            allow_create = False
            allow_fetch = False
            allow_commit = False
            allow_delete = False
            allow_head = False
            allow_list = False

        sot = Test()

        # The first argument to all of these operations is the session,
        # but we raise before we get to it so just pass anything in.
        self.assertRaises(exceptions.MethodNotSupported, sot.create, "")
        self.assertRaises(exceptions.MethodNotSupported, sot.fetch, "")
        self.assertRaises(exceptions.MethodNotSupported, sot.delete, "")
        self.assertRaises(exceptions.MethodNotSupported, sot.head, "")

        # list is a generator so you need to begin consuming
        # it in order to exercise the failure.
        the_list = sot.list("")
        self.assertRaises(exceptions.MethodNotSupported, next, the_list)

        # Update checks the dirty list first before even trying to see
        # if the call can be made, so fake a dirty list.
        sot._body = mock.Mock()
        sot._body.dirty = mock.Mock(return_value={"x": "y"})
        self.assertRaises(exceptions.MethodNotSupported, sot.commit, "")

    def test_unknown_attrs_under_props_create(self):
        class Test(resource.Resource):
            properties = resource.Body("properties")
            _store_unknown_attrs_as_properties = True

        sot = Test.new(
            **{
                'dummy': 'value',
            }
        )
        self.assertDictEqual({'dummy': 'value'}, sot.properties)
        self.assertDictEqual({'dummy': 'value'}, sot.to_dict()['properties'])
        self.assertDictEqual({'dummy': 'value'}, sot['properties'])
        self.assertEqual('value', sot['properties']['dummy'])

        sot = Test.new(**{'dummy': 'value', 'properties': 'a,b,c'})
        self.assertDictEqual(
            {'dummy': 'value', 'properties': 'a,b,c'}, sot.properties
        )
        self.assertDictEqual(
            {'dummy': 'value', 'properties': 'a,b,c'},
            sot.to_dict()['properties'],
        )

        sot = Test.new(**{'properties': None})
        self.assertIsNone(sot.properties)
        self.assertIsNone(sot.to_dict()['properties'])

    def test_unknown_attrs_not_stored(self):
        class Test(resource.Resource):
            properties = resource.Body("properties")

        sot = Test.new(
            **{
                'dummy': 'value',
            }
        )
        self.assertIsNone(sot.properties)

    def test_unknown_attrs_not_stored1(self):
        class Test(resource.Resource):
            _store_unknown_attrs_as_properties = True

        sot = Test.new(
            **{
                'dummy': 'value',
            }
        )
        self.assertRaises(KeyError, sot.__getitem__, 'properties')

    def test_unknown_attrs_under_props_set(self):
        class Test(resource.Resource):
            properties = resource.Body("properties")
            _store_unknown_attrs_as_properties = True

        sot = Test.new(
            **{
                'dummy': 'value',
            }
        )

        sot['properties'] = {'dummy': 'new_value'}
        self.assertEqual('new_value', sot['properties']['dummy'])
        sot.properties = {'dummy': 'new_value1'}
        self.assertEqual('new_value1', sot['properties']['dummy'])

    def test_unknown_attrs_prepare_request_unpacked(self):
        class Test(resource.Resource):
            properties = resource.Body("properties")
            _store_unknown_attrs_as_properties = True

        # Unknown attribute given as root attribute
        sot = Test.new(**{'dummy': 'value', 'properties': 'a,b,c'})

        request_body = sot._prepare_request(requires_id=False).body
        self.assertEqual('value', request_body['dummy'])
        self.assertEqual('a,b,c', request_body['properties'])

        # properties are already a dict
        sot = Test.new(
            **{'properties': {'properties': 'a,b,c', 'dummy': 'value'}}
        )

        request_body = sot._prepare_request(requires_id=False).body
        self.assertEqual('value', request_body['dummy'])
        self.assertEqual('a,b,c', request_body['properties'])

    def test_unknown_attrs_prepare_request_no_unpack_dict(self):
        # if props type is not None - ensure no unpacking is done
        class Test(resource.Resource):
            properties = resource.Body("properties", type=dict)

        sot = Test.new(
            **{'properties': {'properties': 'a,b,c', 'dummy': 'value'}}
        )

        request_body = sot._prepare_request(requires_id=False).body
        self.assertDictEqual(
            {'dummy': 'value', 'properties': 'a,b,c'},
            request_body['properties'],
        )

    def test_unknown_attrs_prepare_request_patch_unpacked(self):
        class Test(resource.Resource):
            properties = resource.Body("properties")
            _store_unknown_attrs_as_properties = True
            commit_jsonpatch = True

        sot = Test.existing(**{'dummy': 'value', 'properties': 'a,b,c'})

        sot._update(**{'properties': {'dummy': 'new_value'}})

        request_body = sot._prepare_request(requires_id=False, patch=True).body
        self.assertDictEqual(
            {u'path': u'/dummy', u'value': u'new_value', u'op': u'replace'},
            request_body[0],
        )

    def test_unknown_attrs_under_props_translate_response(self):
        class Test(resource.Resource):
            properties = resource.Body("properties")
            _store_unknown_attrs_as_properties = True

        body = {'dummy': 'value', 'properties': 'a,b,c'}
        response = FakeResponse(body)

        sot = Test()

        sot._translate_response(response, has_body=True)

        self.assertDictEqual(
            {'dummy': 'value', 'properties': 'a,b,c'}, sot.properties
        )

    def test_unknown_attrs_in_body_create(self):
        class Test(resource.Resource):
            known_param = resource.Body("known_param")
            _allow_unknown_attrs_in_body = True

        sot = Test.new(**{'known_param': 'v1', 'unknown_param': 'v2'})
        self.assertEqual('v1', sot.known_param)
        self.assertEqual('v2', sot.unknown_param)

    def test_unknown_attrs_in_body_not_stored(self):
        class Test(resource.Resource):
            known_param = resource.Body("known_param")
            properties = resource.Body("properties")

        sot = Test.new(**{'known_param': 'v1', 'unknown_param': 'v2'})
        self.assertEqual('v1', sot.known_param)
        self.assertNotIn('unknown_param', sot)

    def test_unknown_attrs_in_body_set(self):
        class Test(resource.Resource):
            known_param = resource.Body("known_param")
            _allow_unknown_attrs_in_body = True

        sot = Test.new(
            **{
                'known_param': 'v1',
            }
        )
        sot['unknown_param'] = 'v2'

        self.assertEqual('v1', sot.known_param)
        self.assertEqual('v2', sot.unknown_param)

    def test_unknown_attrs_in_body_not_allowed_to_set(self):
        class Test(resource.Resource):
            known_param = resource.Body("known_param")
            _allow_unknown_attrs_in_body = False

        sot = Test.new(
            **{
                'known_param': 'v1',
            }
        )
        try:
            sot['unknown_param'] = 'v2'
        except KeyError:
            self.assertEqual('v1', sot.known_param)
            self.assertNotIn('unknown_param', sot)
            return
        self.fail(
            "Parameter 'unknown_param' unexpectedly set through the "
            "dict interface"
        )

    def test_unknown_attrs_in_body_translate_response(self):
        class Test(resource.Resource):
            known_param = resource.Body("known_param")
            _allow_unknown_attrs_in_body = True

        body = {'known_param': 'v1', 'unknown_param': 'v2'}
        response = FakeResponse(body)

        sot = Test()
        sot._translate_response(response, has_body=True)

        self.assertEqual('v1', sot.known_param)
        self.assertEqual('v2', sot.unknown_param)

    def test_unknown_attrs_not_in_body_translate_response(self):
        class Test(resource.Resource):
            known_param = resource.Body("known_param")
            _allow_unknown_attrs_in_body = False

        body = {'known_param': 'v1', 'unknown_param': 'v2'}
        response = FakeResponse(body)

        sot = Test()
        sot._translate_response(response, has_body=True)

        self.assertEqual('v1', sot.known_param)
        self.assertNotIn('unknown_param', sot)
