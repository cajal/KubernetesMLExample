# Kubernetes ML Example
The goal of this doc is to introduce the basic work flow for the new Kubernetes system we will be using phase 3.

This example will cover how to pass credentials into the docker file via environment variables for datajoint, building a docker image and uploading it, and referencing the built docker image in kubernetes for deployment to the cluster.

Code for this tutorial: https://github.com/cajal/KubernetesMLExample.git


# Overview of workflow
1. Develop and test your application via docker on your workstation
2. Once the application is ready for mass deployment, build the docker image base off of your Dockerfile
3. Upload the docker image either to Docker-Hub publicly or to our docker system (Needs to be setup)
4. Create datajoint-credentials and github-credentials secrets for the pods that are to be deploy
5. Create the job yaml file referencing the datajoint-credentials and github-credientials secrets and any other stuff needed like volumes via hostpath
6. Get the .yaml file to at-kubemaster1 somehow, either through github, or just copy and paste, then start it via kubectl create -f <yaml file name> to deploy the job


# Step 1)
## Overview:

This part is really up to you on how you want to approach development of your code, as the only requirement is that you code working directory must be package into a docker container. 

Another way is to write a pod .yaml deployment, and deploy it every time you update the code. In my opinion this is a bit too much work for development, would just prefer you throw it into a jupyter-notebook book docker image base on your work station and work from there.


# Step 2)
## Overview:

The Docker image in this case, should be a bare minimum of what is needed for your code to be run, AKA libraries and dependencies. The code will be clone after the container creation via commands pass from the .yaml file that we will go over later.

Here is the Dockerfile for this example:

![](https://paper-attachments.dropbox.com/s_1658B3DA7264DC308DFF541AD5AF9864461502441102D46F84C863C6F8C40A45_1562582715415_image.png)

# Step 3)
## Overview

In order to build and upload the image above, we would recommend you do it on your workstation machine, as at-kubemaster1 disable docker access for all users as we don’t want anyone messing around with the containers on there.

For this example we will be using my spaceheater machine and docker-hub. This assumes that you already have a docker login and already setup your docker login on your workstation machine by using docker login command

The steps are: 

1. git clone https://github.com/cajal/KubernetesMLExample.git
2. cd KubernetesMLExample/
3. docker build —tag=<Docker_Hub_Username>/kubernetes_ml_example:latest .
4. docker push <Docker_Hub_Username>/kubernetes_ml_example:latest

1-3

![](https://paper-attachments.dropbox.com/s_1658B3DA7264DC308DFF541AD5AF9864461502441102D46F84C863C6F8C40A45_1562583227122_image.png)


4

![](https://paper-attachments.dropbox.com/s_1658B3DA7264DC308DFF541AD5AF9864461502441102D46F84C863C6F8C40A45_1562583931017_image.png)

# Step 4)

K8 secrets requires the value to be encoded in base64, thus you must feed your desired strings into the command echo -n “string_goes_here” | base64  and copy the result to the keys in the secrets .yaml file
Example:

![](https://paper-attachments.dropbox.com/s_1658B3DA7264DC308DFF541AD5AF9864461502441102D46F84C863C6F8C40A45_1562584457388_image.png)


For our use case, we will need two sets of credentials, one for datajoint database server and the other for github login to clone private repository. Both of these yaml file should be made on at-kubemaster1 as you will be running it shortly after creating them to create the secrets

DataJoint:

![](https://paper-attachments.dropbox.com/s_1658B3DA7264DC308DFF541AD5AF9864461502441102D46F84C863C6F8C40A45_1562584686370_image.png)


GitHub:

![](https://paper-attachments.dropbox.com/s_1658B3DA7264DC308DFF541AD5AF9864461502441102D46F84C863C6F8C40A45_1562584770041_image.png)


After creating these files, use kubectl create -f <file_name.yaml> to create both secrets.
Upon successful creation of both secrets, you should confirm by using kubectl get secrets

![](https://paper-attachments.dropbox.com/s_1658B3DA7264DC308DFF541AD5AF9864461502441102D46F84C863C6F8C40A45_1562584929176_image.png)

# Step 5)

Now we can create the job.yaml file, in this case it is name job_deployment.yaml in the github repository.

![](https://paper-attachments.dropbox.com/s_1658B3DA7264DC308DFF541AD5AF9864461502441102D46F84C863C6F8C40A45_1562585039300_image.png)


If you don’t understand some parts of it, I would recommend you read through the docs about K8 secrets and commands

https://kubernetes.io/docs/concepts/configuration/secret/

https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/



# Step 6)

For this part, you can place the yaml file you created in part 5 in your github respo, or just ssh in at-kubemaster1 and make a new yaml file via nano and paste the content over.

After that you can create the job via kubectl create - f <yaml file name>

![](https://paper-attachments.dropbox.com/s_1658B3DA7264DC308DFF541AD5AF9864461502441102D46F84C863C6F8C40A45_1562585411330_image.png)



# To deploy updates:

Lets say you have a new version of your code you want to deploy to the cluster. For this the steps are pretty straight forward. All you need it is to push the new version of your code up, delete the current job and relaunch it. The reason why this works is that we setup the pod to clone the repository each time, thus fetching the newest version of your code. No need to rebuild the image which takes forever.


# Mounting scratch and stores

For this, we would recommend using hostpath to deal with this. Yes this does assume that every worker node on the cluster have the drive mounting correctly, but they should be via the salt recipe. If they are not please report to the kubernetes channel so the administrators can resolve the issue.

https://kubernetes.io/docs/concepts/storage/volumes/#hostpath

