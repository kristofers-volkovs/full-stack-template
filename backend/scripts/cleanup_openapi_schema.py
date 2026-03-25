import json

# NOTE: split key needs to be updated if the version is bumped
split_key = "_api_v1_"


def handle_string_split(*, name: str):
    split_list = name.split(split_key)

    if len(split_list) <= 1:
        raise ValueError(f"Error, split_list value is <=1 and name: {name}")

    return split_list[0]


openapi_json_path = "src/openapi.json"
data = json.loads(open(openapi_json_path).read())

if "paths" not in data:
    raise ValueError(f"Error, 'paths' missing from data, keys: {data.keys()}")

paths_data = data["paths"]
for url_key, https_methods in paths_data.items():
    for method_key, method_metadata in https_methods.items():
        if "operationId" not in method_metadata:
            raise ValueError(
                f"Error, 'operationId' missing from method_metadata, keys: {method_metadata.keys()}"
            )

        operation_id = method_metadata["operationId"]
        new_operation_id = handle_string_split(name=operation_id)

        data["paths"][url_key][method_key]["operationId"] = new_operation_id

        if "requestBody" in method_metadata:
            request_body = method_metadata["requestBody"]
            if "content" not in request_body:
                raise ValueError(
                    f"Error, 'content' missing from request_body, keys: {request_body.keys()}"
                )

            request_body_content = request_body["content"]
            for content_key, content_metadata in request_body_content.items():
                if "schema" not in content_metadata:
                    raise ValueError(
                        f"Error, 'schema' missing from content_metadata, keys: {content_metadata.keys()}"
                    )

                schema = content_metadata["schema"]
                if "$ref" not in schema:
                    raise ValueError(
                        f"Error, '$ref' missing from schema, keys: {schema.keys()}"
                    )

                ref = schema["$ref"]
                if split_key in ref:
                    new_ref = handle_string_split(name=ref)
                    data["paths"][url_key][method_key]["requestBody"]["content"][
                        content_key
                    ]["schema"]["$ref"] = new_ref

if "components" not in data:
    raise ValueError(f"Error, 'components' missing from data, keys: {data.keys()}")

components_data = data["components"]

if "schemas" not in components_data:
    raise ValueError(
        f"Error, 'schemas' missing from components_data, keys: {components_data.keys()}"
    )

schemas = components_data["schemas"]

schema_keys_to_update = []
for schema_key, _schema_metadata in schemas.items():
    if split_key in schema_key:
        schema_keys_to_update.append(schema_key)

for schema_key in schema_keys_to_update:
    schema_metadata = schemas[schema_key]
    if "title" not in schema_metadata:
        raise ValueError(
            f"Error, 'title' missing from schema_metadata, keys: {schema_metadata.keys()}"
        )

    schema_title = schema_metadata["title"]
    new_schema_key = handle_string_split(name=schema_key)
    new_schema_title = handle_string_split(name=schema_title)

    schema_metadata["title"] = new_schema_title
    data["components"]["schemas"][new_schema_key] = schema_metadata
    del data["components"]["schemas"][schema_key]

json.dump(data, open(openapi_json_path, "w"), indent=4)
