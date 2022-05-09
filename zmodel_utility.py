from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.fields.reverse_related import ManyToOneRel
from django.db.models.fields.related import OneToOneRel, ManyToManyField

__author__ = 'Sathananthan A'
__email__ = 'sathananthanit@gmail.com'
__version__ = '0.1.0'
__title__ = 'Model Utility'
__description__ = 'Django Model Related Utility Classes and Functions'
__python__ = 3.8
__django__ = 3.2


class InvalidKeyLookup(Exception): pass
class InvalidModelClass(Exception): pass
class Empty: pass
class OneToOneObject: pass
class ManyToOneObject: pass
class ManyToManyObject: pass


class GetModelData:
	'''
	Description :
		Provide Django Model Instance Data as dict or list

	Code Flow :
		GetModelData
		|__ __init__()
		    |__self._check_valid_model_klass()
		    |__self._set_unique_fields()
		    |__self._check_omit_and_only_fields()

		|__self.to_dict() or self.to_list()
		   |__self._prepare_output()
			  |__self._get_object()
			     |__self._check_key()
			  |__self._collect_data()
			     |__self._get_fields()
			  or
			  |__self._collect_relational_data()
			     |__self._get_fields_with_lookup()

		|__cls.from_db()
		   |__GetModelData().to_dict() or to_list()

	Dependency Types :
		InvalidKeyLookup  - Throw error when key is invalid (not found in instance)
		InvalidModelClass - Throw error when model is invalid (not a subclass of models.Model)
		Empty             - Set this type when data is insufficient
		OneToOneObject    - Set this flag to field if field is related with O2O field
		ManyToOneObject   - Set this flag if field is related with M2O field
		ManyToManyObject  - Set this flag if field is related with M2M field

	Developed On :
		Python 3.8
		Django 3.2
	'''
	def __init__(self, model_klass, *, key=None, value=None, omit=None, only=None, rel=False):
		'''
		Parameters :
			model_klass -> Django Model Type
			key         -> Object Lookup Key
			value       -> Query Filter Value
			omit        -> List of fields should not be included in result
			only        -> List of fields only included in result
			rel         -> Get all data from M2M, O2O, M2O fields

		Methods :
			self._check_valid_model_klass
				Verify the "model_klass" value is Subclass of models.Model
			
			self._set_unique_fields
				Check and Set unique fields in instance named as "_unique_fiedls"

			self._check_omit_and_only_fields
				Cross-check if omit and only fields are exists in model fields
			
			cls.from_obj()
				Returns data based on object
		'''
		self._model = model_klass
		self._key = key
		self._value = value
		self._omit = omit or []
		self._only = only or []
		self._rel = rel

		self._check_valid_model_klass()
		self._set_unique_fields()
		self._check_omit_and_only_fields()

	def _check_valid_model_klass(self):
		try:
			if models.Model not in self._model.__mro__:
				raise InvalidModelClass(
				f'The Model Class {self._model} is invalid, '
				f'Provide valid django model class'
			)
		except:
			raise InvalidModelClass(
				f'The Model Class {self._model} is invalid, '
				f'Provide valid django model class'
			)

	def _set_unique_fields(self):
		unique_fields = []
		for field in self._model._meta.local_fields:
			if field.unique: unique_fields.append(field.name)
		setattr(self, '_unique_fields', unique_fields)

	def _check_omit_and_only_fields(self):
		fields = self._get_fields()
		if self._omit and isinstance(self._omit, (list, tuple)):
			for field in self._omit:
				if field not in fields:
					raise InvalidKeyLookup(
						f'Omit list contain invalid field "{field}"'
					)
		if self._only and isinstance(self._only, (list, tuple)):
			for field in self._only:
				if field not in fields:
					raise InvalidKeyLookup(
						f'Only list contain invalid field "{field}"'
					)
		if self._omit and not isinstance(self._only, (list, tuple)):
			raise ValueError('omit must be list or tuple of strings')
		if self._only and not isinstance(self._only, (list, tuple)):
			raise ValueError('only must be list or tuple of strings')
		
		for field in self._omit:
			if field in self._only:
				raise ValueError(
					f'omit and only fields cannot be same'
					f'field "{field}" either in only or in omit'
				)

	def _get_fields(self):
		return [field.name for field in self._model._meta.local_fields]

	def _get_fields_with_lookup(self):
		fields = {}
		for field in self._model._meta.get_fields():
			if field.__class__ == ManyToOneRel:
				fields.update({field.name: ManyToOneObject})
			elif field.__class__ == ManyToManyField:
				fields.update({field.name: ManyToManyObject})
			elif field.__class__ == OneToOneRel:
				fields.update({field.name: OneToOneObject})
			else:
				fields.update({field.name: f'{field.name}'})
		return fields

	def _check_key(self):
		if self._key not in self._unique_fields:
			raise InvalidKeyLookup(
				f'The {self._model} Type does not have field "{self._key}",'
				f' Use one of those fields in this list {self._unique_fields}'
			)

	def _get_object(self):
		query = {self._key: self._value}
		self._check_key()
		try:
			obj = self._model.objects.get(**query)
			return obj
		except ObjectDoesNotExist:
			return {}
		except Exception as exc:
			raise Exception from exc

	def _collect_data(self, obj):
		data = {}
		for field in self._get_fields():
			try:
				data[field] = eval(f'obj.{field}')
			except:
				data[field] = Empty
		return data

	def _collect_relational_data(self, obj):
		fields = self._get_fields_with_lookup()
		data = {}
		for fname, fvalue in fields.items():
			try:
				if fvalue == OneToOneObject:
					o2o_obj = eval(f'obj.{fname}')
					data[fname] = GetModelData.from_obj(o2o_obj)
				elif fvalue == ManyToOneObject:
					m2o_objs = eval(f'obj.{fname}_set.all()')
					data[fname] = []
					for _obj in m2o_objs:
						data[fname].append(GetModelData.from_obj(_obj))
				elif fvalue == ManyToManyObject:
					m2m_objs = eval(f'obj.{fname}.all()')
					data[fname] = []
					for _obj in m2m_objs:
						data[fname].append(GetModelData.from_obj(_obj))
				else:
					data[fname] = eval(f'obj.{fname}')
			except:
				data[fname] = Empty
		return data

	def _prepare_output(self):
		obj = self._get_object()
		if not obj: return obj
		if self._rel:
			data = self._collect_relational_data(obj)
		else:
			data = self._collect_data(obj)

		only_data = {}
		if self._omit:
			for field in self._omit:
				data.pop(field)
		if self._only:
			for field in self._only:
				only_data[field] = data[field]
			return only_data
		return data

	def to_dict(self):
		'''Returns object data as dictionary'''
		return self._prepare_output()

	def to_list(self):
		'''Returns object data as list'''
		return [(key, value) for key, value in self._prepare_output().items()]
	
	@classmethod
	def from_obj(cls, obj, omit=None, only=None, _type='dict', rel=False):
		'''Quick class method to get data from object. It returns data based on _type'''
		data = GetModelData(
			obj.__class__, key='id', value=obj.id, omit=omit, only=only, rel=rel
		)
		if _type == 'dict':
			return data.to_dict()
		elif _type == 'list':
			return data.to_list()
		else:
			raise NotImplementedError(f'The method to_{_type} not implemented')


def obj_data(model_klass,*, key, value, omit=None, only=None, _type='dict', rel=False):
	'''A wrapper function over GetModelData and returns single data'''
	obj = GetModelData(
		model_klass, key=key, value=value, omit=omit, only=only, rel=rel
	)
	if _type == 'dict':
		return obj.to_dict()
	elif _type == 'list':
		return obj.to_list()
	else:
		raise NotImplementedError(f'The method to_{_type} not implemented')


def list_of_obj_data(obj_list,*, only=None, omit=None, _type='dict', rel=False):
	'''A wrapper function over GetModelData and returns list of data'''
	data = []
	for _obj in obj_list:
		obj = GetModelData(
			_obj.__class__, key='id', value=_obj.id, only=only, omit=omit, rel=rel
		)
		if _type == 'dict': data.append(obj.to_dict())
		elif _type == 'list': data.append(obj.to_list())
		else: raise NotImplementedError(f'The method to_{_type} not implemented')
	return data
