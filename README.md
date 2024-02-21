# Instrument Drivers
This repository contains python based SweepMe! ([https://sweep-me.net/](https://sweep-me.net/)) instrument drivers. 
SweepMe! is a test&measurement software that allows users to quickly combine instruments from different vendors in a low-code/no-code environment.
The software has an open driver interface so that everybody can work on own driver implementations or modify existing drivers.
**But: The drivers in this repository are for developers only.**
All users of SweepMe! can download versioned drivers from our server via the included version manager.

To get started with SweepMe!, please visit the 'First steps' article of our [Wiki](https://wiki.sweep-me.net/wiki/Main_Page).

## Development guide
Our Wiki contains a section about [Driver Programming](https://wiki.sweep-me.net/wiki/Driver_Programming) where you can find a description of the driver API.

Simple modifications can be done without using this repository.
Just right-click a version in SweepMe!'s version manager and use "Create custom version".
This will copy the driver to a public folder on your driver. Activate this custom version and start working on it.

## Loading repository drivers with SweepMe!

* Update SweepMe! to version 1.5.6.12 or higher
* Clone the instrument-drivers repository to your local drive
* Add a Windows PATH system variable "SWEEPME_REPO_DRIVERS" and link it to the folder src of the repository that contains all drivers 
* After restarting SweepMe!, the version manager (menu "Tools" -> "Modules & Devices") is now listing also version labeled with the origin "repo".
* Activate those driver versions from the repo if you like to test and work on them.

## Contribution
We would be happy to add your SweepMe! instrument driver to this repository and make it thus freely available to all other users.
If you like to contribute your revised or newly created driver, it is basically possible to contribute them via a pull request.
Before we add you to the group of users that can make pull requests, we need your contribution agreement.
Especially, if you are an employee of a company or a university, the code often belongs to your employee which needs to agree as well to the contribution.
Please contact us via contact@sweep-me.net to clarify your employment situation.

Besides contributing via a pull request, it is also possible to contribute by sending the driver by email, and we will add it to the repository and release new version on our server.
This often the easier solution for everyone who is not familiar with using git repositories.

Companies can sign individual contribution agreements that allow us to release the drivers of their coworkers without being reliable for the content as we will check it and release it under our name. 

In any case, the contributor will be named, unless otherwise requested.

## Licensing
Whenever possible we try to release all instrument drivers with a generous [MIT license](https://opensource.org/license/mit/).
However, sometimes this is not possible because the sub-dependencies come with their own licenses/restrictions. 
Or the commands of the instruments are not publicly available, and then we are not allowed to redistribute the driver without permission by the instrument manufacturer.
This means that each driver comes with an own license file and can contain further license files of their sub-dependencies.
There is no general license for all drivers.
To still keep the licensing of the drivers as homogeneous as possible we try to use as much as possible MIT license and only
accept drivers with MIT license if it is basically possible to use this license. 
In case of questions, just contact us via contact@sweep-me.net and we can cross-check the licensing situation.

Besides using sub-dependencies, i.e. third-party libraries, it can be also the case that you have copied code parts
from other repositories or from stack-overflow. Please, indicate such parts with a comment if they have some inventive step
and go beyond the standard use of the programming language. 
For example, copying a function from another third-party library one-to-one would require to check and add the license of this library as well.
Best solution is often to re-write and restructure such parts with own code to make sure it is your own individual work.

An overview about different license types and how to handle them can be found in our [License driver guide](https://wiki.sweep-me.net/wiki/License_Guide_for_Drivers).





