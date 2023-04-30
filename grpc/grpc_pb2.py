# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: grpc.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='grpc.proto',
  package='grpc',
  syntax='proto3',
  serialized_options=b'\242\002\003HLW',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\ngrpc.proto\x12\x04grpc\"+\n\nJobMessage\x12\r\n\x05\x62\x61tch\x18\x01 \x01(\x05\x12\x0e\n\x06q_wait\x18\x02 \x01(\x02\"<\n\x0bServerReply\x12\x10\n\x08\x65xe_time\x18\x01 \x01(\x02\x12\x0b\n\x03idx\x18\x02 \x01(\x05\x12\x0e\n\x06q_wait\x18\x03 \x01(\x02\x32;\n\tScheduler\x12.\n\x05Serve\x12\x10.grpc.JobMessage\x1a\x11.grpc.ServerReply\"\x00\x42\x06\xa2\x02\x03HLWb\x06proto3'
)




_JOBMESSAGE = _descriptor.Descriptor(
  name='JobMessage',
  full_name='grpc.JobMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='batch', full_name='grpc.JobMessage.batch', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='q_wait', full_name='grpc.JobMessage.q_wait', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=20,
  serialized_end=63,
)


_SERVERREPLY = _descriptor.Descriptor(
  name='ServerReply',
  full_name='grpc.ServerReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='exe_time', full_name='grpc.ServerReply.exe_time', index=0,
      number=1, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='idx', full_name='grpc.ServerReply.idx', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='q_wait', full_name='grpc.ServerReply.q_wait', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=65,
  serialized_end=125,
)

DESCRIPTOR.message_types_by_name['JobMessage'] = _JOBMESSAGE
DESCRIPTOR.message_types_by_name['ServerReply'] = _SERVERREPLY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

JobMessage = _reflection.GeneratedProtocolMessageType('JobMessage', (_message.Message,), {
  'DESCRIPTOR' : _JOBMESSAGE,
  '__module__' : 'grpc_pb2'
  # @@protoc_insertion_point(class_scope:grpc.JobMessage)
  })
_sym_db.RegisterMessage(JobMessage)

ServerReply = _reflection.GeneratedProtocolMessageType('ServerReply', (_message.Message,), {
  'DESCRIPTOR' : _SERVERREPLY,
  '__module__' : 'grpc_pb2'
  # @@protoc_insertion_point(class_scope:grpc.ServerReply)
  })
_sym_db.RegisterMessage(ServerReply)


DESCRIPTOR._options = None

_SCHEDULER = _descriptor.ServiceDescriptor(
  name='Scheduler',
  full_name='grpc.Scheduler',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=127,
  serialized_end=186,
  methods=[
  _descriptor.MethodDescriptor(
    name='Serve',
    full_name='grpc.Scheduler.Serve',
    index=0,
    containing_service=None,
    input_type=_JOBMESSAGE,
    output_type=_SERVERREPLY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_SCHEDULER)

DESCRIPTOR.services_by_name['Scheduler'] = _SCHEDULER

# @@protoc_insertion_point(module_scope)