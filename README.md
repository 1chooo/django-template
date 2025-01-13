# Django Template

## Requirements Extensions

- python development extensions(e.g. `ms-python.python`, `ms-python.vscode-pylance`, etc.)
- [editorconfig](https://marketplace.visualstudio.com/items?itemName=EditorConfig.EditorConfig)
- [ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

## Recommended Extensions

- [Code Spell Checker](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker)
- [Doxygen Documentation Generator](https://marketplace.visualstudio.com/items?itemName=cschlosser.doxdocgen)

## Core Dependencies

- python 3.12
- django 5.1

## The beginning of everything

1. install `python3.12` and `poetry` if you don't have it, and make sure you poetry config is set to `virtualenvs.in-project = true`.

2. create a virtual environment. for example:

    ```shell
    poetry env use python3.12
    python3.12 -m venv .venv
    ```

    -  If you are using Windows, please use these commands

        ```shell
        python -m venv .venv
        py -3.12 -m venv .venv
        ```

3. install the dependencies. for example:

    ```shell
    poetry install
    poetry install --with=lint
    poetry install --with=dev
    poetry install --with=lint --with=dev
    ```

4. activate the virtual environment.

5. install the pre-commit hooks.

   ```shell
   pre-commit install
   ```

PS. can also use `pre-commit run --all-files` to run the pre-commit hooks manually.

## How to run locally

1. make sure already installed the dependencies.
2. make sure already copy the `.env.example` in `./dotenv` to `.env` and set the environment variables. also all dependencies services are running.
3. activate the virtual environment.
4. run the server.

   ```shell
   python manage.py runserver
   ```

   or run the asynchronous server with uvicorn.

   ```shell
   python -m uvicorn config.asgi:application
   ```

   if you want to use the auto-reload feature, you can add the `--reload` flag.

   ```shell
   python -m uvicorn config.asgi:application --reload
   ```

## How to run celery related services

1. make sure already installed the dependencies.
2. make sure already copy the `.env.example` in `./dotenv` to `.env` and set the environment variables. also all dependencies services are running.activate the virtual environment.
3. run the celery.

   ```shell
   celery -A config worker -l info -E
   ```

   -  If your system is Windows, please use the following code to test

      ```shell
      celery -A config worker --pool=solo --loglevel=info
      ```

   -  inspect the tasks.

      ```shell
      celery -A config inspect registered
      ```

   -  call the tasks.
      ```shell
      celery -A config call <task_name> -a <args>
      ```

> [!NOTE]
> There are some celery relative services such as `celery-beat`, `celery-flower`, etc. Please refer to the [celery documentation](https://docs.celeryproject.org/en/stable/index.html) for more information.

## How to migrate models to database

1. make sure already installed the dependencies.
2. make sure already copy the `.env.example` in `./dotenv` to `.env` and set the environment variables. also all dependencies services are running.
3. activate the virtual environment.
4. make migrations.

   ```shell
   python manage.py makemigrations
   ```
5. migrate the models to the database.

   ```shell
   python manage.py migrate
   ```

## Note
> [!NOTE]
> -  every model must inherit `BaseModel` in `common.models`.
> -  every admin register class must inherit `BaseAdmin` in `common.admin`.
