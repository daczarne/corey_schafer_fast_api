# Corey Schafer's FastAPI tutorial

This is a code-along repository for Corey Schafer's fastAPI tutorial series. The videos can be found in the following
links:

1. [Getting started][getting-started]
1. [Jinja2 templates][jinja2-templates]
1. [Path parameters][path-parameters]
1. [Pydantic schemas][pydantic-schemas]
1. [SQLAlchemy models and relationships][sqlalchemy-models-and-relationships]
1. [Completing CRUD][completing-crud]
1. [Async][async]
1. [Routers][routers]

## Status code used

- **200 OK**: successful `GET`, `PUT`, or `PATCH`
- **201 Created**: successful `POST` for users and posts
- **204 No Content**: successful `DELETE`
- **400 Bad Request**: duplicated username/email when creating users
- **404 Not Found**: resource doesn't exist (user or post)
- **422 Unprocessable Entity**: validation error (automatic from Pydantic)

## Authentication and authorization

- Authentication: who are you?
- Authorization: what are you allowed to do?

How to generate good secrete keys in the terminal?

```shell
python -c "import secrets; print(secrets.token_hex(32))"
```

[getting-started]: https://www.youtube.com/watch?v=7AMjmCTumuo
[jinja2-templates]: https://www.youtube.com/watch?v=G4NIB9Rx9Qs
[path-parameters]: https://www.youtube.com/watch?v=WRjXIA5pMtk
[pydantic-schemas]: https://www.youtube.com/watch?v=9GHxnttXxrA
[sqlalchemy-models-and-relationships]: https://www.youtube.com/watch?v=NvOV3ig2tGY
[completing-crud]: https://www.youtube.com/watch?v=VyoGAoxQhxM
[async]: https://www.youtube.com/watch?v=2JPDt-Jp6fM
[routers]: https://www.youtube.com/watch?v=NkgIHa6KtHg
