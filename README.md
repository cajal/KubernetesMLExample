# Kubernetes ML Example
The goal of this doc is to introduce the basic work flow for the new Kubernetes system we will be using phase 3.

This example will cover how to pass credentials into the docker file via environment variables for datajoint, building a docker image and uploading it, and referencing the built docker image in kubernetes for deployment to the cluster.

Code for this tutorial: https://github.com/cajal/KubernetesMLExample.git


# Two Options for deploying
1) Docker Image Build
2) Github Branch Reference

## What is the differnce
The reason for the two options have mostly deals with the way code should be handle when using kubernetes. In both cases however, before pushing an update, the user's should stop the current job before either uploading the docker image or commiting to the master branch of the code respository.

For the docker image build option, everytime the deployment ready code is to be updated, the user must rebuild their image and uploaded it to their Docker Registry before the changes are picked up by new pods.
As for the Github Master Branch option, the point of update will be the master branch, thus any new commits apply to the master branches will cause all new pods being launched to use the new code base.

Our recommendation is with the docker image build option if the user is not familiar with github branches, as there is pretty good chance that if the users commit the wrong branch, it might ruin the current job relabilty.
