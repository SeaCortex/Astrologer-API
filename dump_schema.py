from app.main import app
import json


def dump_schema(output_file_path):
    openapi_data = app.openapi()

    with open(output_file_path, "w") as file:
        json.dump(openapi_data, file, indent=2)


if __name__ == "__main__":
    # https://editor-next.swagger.io/
    dump_schema("openapi.json")
    print("OpenAPI JSON file generated successfully! Check it here: https://editor-next.swagger.io/")
