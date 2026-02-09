# CH00 Development Guideline
version: 0.0.1

## Specification
User requirements are named UReq<Number>.
System requirement are named SReq<Number>.

Code and test may implements directly User Requirement (UReq). If needed, some System Requirements may refine some user requirements according to certain technical or design choices. 

The development of coco application must ensure traceability and allow to visualize coverage matrix:
- how SReq covers UReq
- how code implement SReq or UReq
- how test verifies the code implementing the SReq or UReq

Each UReq and SReq must have a 2 digit version number: 1st digit for major or incompatible changes, 2nd digit for smaller modification. Example: v1.2
Status of each UReq and SReq must be maintained. The status are : specified, refined, implemented, tested, reviewed, complete 

## Coding
The coding language used for coco application is mainly python language.
All source code must be written in english, this applied for comments, module names, class names, variables names, function names etc ...
Code Cleaning principle described by Arthur C.Martins (alias Uncle Bob) must be applied.

## Testing
All production code must be at least tested or reviewed before it is considered ready for production delivery

Test folder must be separated from the src folder which contain production code.

## .venv
2 virtual environments, env1 and env2 will be defined and used. env1 for usual development, and env2 to evaluate impact of upgrading or downgrading to certain library version number.

## Project Structure

project_root
	- \src : folder containing all production code
	- \tests: folder containing unit tests
	- \tests-it: folder containing integration test
	- \tests-e2e: folder containing end to end tests
	- \resources: folder containing example files or folders
	- \doc : folder containing project documentation. This folder contains itself several subfolders:
		- \spec : folder containing specifications
		- \userdoc: folder containing user documentation
		- \design: folder containing documentation for architecture, design choices, and technical tricks 
		- \Delivery : folder containing markdown page resuming the delivered release and their features.

## Code Quality
All code must be checked using SonarQube, pylint, mypy (http://mypy-lang.org), black (https://github.com/pfs/black)	
User Requirement coverage matrix for refinement, implementation, testing must be provided.

## Deployment
A build script will check code quality and produce a standalone executable file as well as user documentation that may be shipped on a delivery space with release note. 
