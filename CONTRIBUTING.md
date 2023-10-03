# Questions

If you are having difficulties using the APIs or have a question about the IBM Cloud and Services,
please ask a question on [dW Answers][dw] or [Stack Overflow][stackoverflow].

# Issues

If you encounter an issue with the Python Core SDK, you are welcome to submit a [bug report](https://github.com/IBM/python-sdk-core/issues).
Before that, please search for similar issues. It's possible somebody has encountered this issue already.

# Code
## Commit Messages
Commit messages should follow the [Angular Commit Message Guidelines](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#-commit-message-guidelines).
This is because our release tool - [semantic-release](https://github.com/semantic-release/semantic-release) -
uses this format for determining release versions and generating changelogs.
Tools such as [commitizen](https://github.com/commitizen/cz-cli) or [commitlint](https://github.com/conventional-changelog/commitlint)
can be used to help contributors and enforce commit messages.
Here are some examples of acceptable commit messages, along with the release type that would be done based on the commit message:

| Commit message                                                                                                                                                              | Release type               |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------|
| `fix(IAM Authentication) propagate token request errors back to request invocation thread`                                                                                  | Patch Release              |
| `feat(JSON Serialization): add custom deserializer for dynamic models`                                                                                                      | ~~Minor~~ Feature Release  |
| `feat(BaseService): added baseURL as param to BaseService ctor`<br><br>`BREAKING CHANGE: The global-search service has been updated to reflect version 3 of the API.`       | ~~Major~~ Breaking Release |

# Pull Requests

If you want to contribute to the repository, here's a quick guide:

1. Fork the repository
1. Install `virtualenv` and `tox`
1. Develop and test your code changes with [pytest].
    * Respect the original code [style guide][styleguide].
    * Only use spaces for indentation.
    * Create minimal diffs - disable on save actions like reformat source code or organize imports. If you feel the source code should be reformatted create a separate PR for this change.
    * Check for unnecessary whitespace with `git diff --check` before committing.
    * Make sure your code tests clean on the project's supported versions of Python.  You can use the `venv` module to create virtual environments for this.
1. Make the test pass
    *  Linting errors can be fixed by running `make lint-fix` in most cases
1. Check code coverage. Add tests for all new functionality and ensure overall coverage does not decrease.
1. Commit your changes
* Commits should follow the [Angular commit message guidelines](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#-commit-message-guidelines). This is because our release tool uses this format for determining release versions and generating changelogs. To make this easier, we recommend using the [Commitizen CLI](https://github.com/commitizen/cz-cli) with the `cz-conventional-changelog` adapter.
1. Push to your fork and submit a pull request to the `dev` branch

# Running the tests

It is STRONGLY recommended that you set up and use a [virtualenv].

1. Clone this repository:
    ```sh
    git clone git@github.com:IBM/python-sdk-core.git
    ```
1. Create a virtual environment:
   ```sh
   python -m venv ./venv3    # create venv in directory './venv3' using "python" command
   . venv3/bin/activate      # establish venv's environment
   python -V                 # check version of "python" command in venv
   ```
1. Install the project dependencies and install the project as an editable package using the current source:
    ```sh
    make setup
    ```
1. Run the unit tests:
    ```sh
    make test-unit
    ```
1. Run the lint checks on the source code:
    ```sh
    make lint
    ```
1. Run the code formatter on the source code to ensure compliance with the linter:
    ```sh
    make lint-fix
    ```
1. Run the entire build (install dependencies, run unit tests and perform lint checks):
    ```sh
    make all
    ```

# Developer's Certificate of Origin 1.1
By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
   have the right to submit it under the open source license
   indicated in the file; or

(b) The contribution is based upon previous work that, to the best
   of my knowledge, is covered under an appropriate open source
   license and I have the right under that license to submit that
   work with modifications, whether created in whole or in part
   by me, under the same open source license (unless I am
   permitted to submit under a different license), as indicated
   in the file; or

(c) The contribution was provided directly to me by some other
   person who certified (a), (b) or (c) and I have not modified
   it.

(d) I understand and agree that this project and the contribution
   are public and that a record of the contribution (including all
   personal information I submit with it, including my sign-off) is
   maintained indefinitely and may be redistributed consistent with
   this project or the open source license(s) involved.

# Additional Resources

* [General GitHub documentation](https://help.github.com/)
* [GitHub pull request documentation](https://help.github.com/send-pull-requests/)

[dw]: https://developer.ibm.com/answers/questions/ask.html
[stackoverflow]: http://stackoverflow.com/questions/ask?tags=ibm
[styleguide]: http://google.github.io/styleguide/pyguide.html
[pytest]: http://pytest.org/latest/
[virtualenv]: http://virtualenv.readthedocs.org/en/latest/index.html
