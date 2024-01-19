Project was developed fully using TDD.
Repository pattern is used for persistent sqlite repository.
run python -m library.runner --host 127.0.0.1 --port 9000 from path right above library folder.
After running above command, write http://127.0.0.1:9000/docs in your browser to access the docs.


Files and their explanations:
./infra
    ./infra/fastapi
        ./infra/fastapi/entities.py - contains all post/get/patch/delete resources for FasAPI
        ./infra/fastapi/base_models.py - classes here mimic ones in ./core/entities.py with minor modifications.
        ./infra/fastapi/dependables.py - defined repository dependable for FasAPI.
    ./infra/repository
        ./infra/repository/repository.py - repository protocol. repository only has simple database query/modify mechanisms,
        a bit more than CRUD for our purposes, but any other processing is pushed out to the Service class in ./core directory.
        ./infra/repository/persistent_repo
            ./infra/repository/persistent_repo/repository.py - one implementation for protocol - persistent in SQLite.
./runner
    ./runner/cli.py - taken from session 15 code.
    ./runner/setup.py -  taken from session 15 code.
./tests
    ./tests/conftest.py - contains fixtures. This filename is specifically known to pytest so do not modify.
    ./tests/tests.py - All tests are in one file as opposed to multiple for sake of simple run. All tests mimic all the requests (plus more) given in assignment text.
    ./tests/fakes.py - Fake entities are declared, only to be used for testing purposes.
./core
    ./core/entities.py - contains value classes and protocol for any 'data type' needed for the assignment.
    ./core/errors.py - self-explanatory.
    ./core/serialization.py - provides serialization for db. In the beginning, I was saving the list as column in my db, so my serialization class was extremely
    complicated. But since I removed list-as-a-column approach and created new table instead, serialization class became much simpler.
    ./core/service.py - FastAPI requests do not directly have access to repository. they do this through the service class.
