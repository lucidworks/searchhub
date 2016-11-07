The main bootstrapping code, bootstrap.py in the python directory, currently relies on certain conventions for files in this directory.

1. It can only load files ending with file extension ```.json```
1. All pipeline definitions must end with ```_pipeline.json```
1. All query pipelines must also have the word ```query``` in them.  If it is not present, the bootstrap will assume it is an index pipeline
1. All schedule definitions must end with ```_schedule.json```
1. All search compoonents definitions must end with ```_search_components.json```
1. All request handler definitions must end with ```_request_handler.json```
1. All field type definitions must end with ```_field_type.json```
1. Any taxonomy definition must be named ```taxonomy.json```

At some point in the future, we will probably switch to a sub directory structure
or some other means of organizing these files.
