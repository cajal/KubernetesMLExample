# Docker Build Option
For this option, the moment the user pushes the rebuilt image with their new code to the docker respository, any new pods created will download that updated


# Overview of workflow
1. Develop and test the user's application via docker on the user's workstation
2. Once the application is ready for mass deployment, build the docker image base off of the user's Dockerfile which will also clone the respo with the GitHub credientals provided 
3. Upload the docker image either to Docker-Hub publicly or to our docker system (Needs to be setup)
4. Create datajoint-credentials for the pods that are to be deploy
5. Create the job yaml file referencing the datajoint-credentials secrets and any other stuff needed like volumes via hostpath
6. Get the .yaml file to at-kubemaster1 somehow, either through github, or just copy and paste, then start it via kubectl create -f file_name.yaml to deploy the job


# Step 1)
## Overview:

This part is really up to the user on how the user want to approach development of the user's code, as the only requirement is that the user code working directory must be package into a docker container. 

Another way is to write a pod .yaml deployment, and deploy it every time the user update the code. In my opinion this is a bit too much work for development, would just prefer the user throw it into a jupyter-notebook book docker image base on the user's work station and work from there.


# Step 2)
## Overview:

The Docker image in this case, should be a bare minimum of what is needed for the user's code to be run, AKA libraries and dependencies. The code will be clone after the container creation via commands pass from the .yaml file that we will go over later.

Here is the Dockerfile for this example:

![](https://paper-attachments.dropbox.com/s_807C4A1ACAEC7AEF0E446757A97CF7C3E28D540808B6336A2DC463F7C20352FD_1562709275620_image.png)

# Step 3)
## Overview

In order to build and upload the image above, we would recommend the user do it on the user's workstation machine, as at-kubemaster1 disable docker access for all users as we don’t want anyone messing around with the containers on there.

For this example we will be using my spaceheater machine and docker-hub. This assumes that the user already have a docker login and already setup the user's docker login on the user's workstation machine by using docker login command

The steps are: 

1. git clone https://github.com/cajal/KubernetesMLExample.git
2. cd KubernetesMLExample/docker_build_option
3. docker build --build-arg GITHUB_USERNAME=\<your_username> --build-arg GITHUB_PASSWORD=\<your_password> —tag=\<Docker_Hub_Username>/kubernetes_ml_example_docker:latest .
4. docker push \<Docker_Hub_Username>/kubernetes_ml_example_docker:latest

1-3

![](https://paper-attachments.dropbox.com/s_807C4A1ACAEC7AEF0E446757A97CF7C3E28D540808B6336A2DC463F7C20352FD_1562711150983_image.png)


4

![](https://paper-attachments.dropbox.com/s_807C4A1ACAEC7AEF0E446757A97CF7C3E28D540808B6336A2DC463F7C20352FD_1562712070308_image.png)

# Step 4)

K8 secrets requires the value to be encoded in base64, thus the user must feed the user's desired strings into the command echo -n \<string_to_encode> | base64  and copy the result to the keys in the secrets .yaml file
Example:

![](https://paper-attachments.dropbox.com/s_1658B3DA7264DC308DFF541AD5AF9864461502441102D46F84C863C6F8C40A45_1562584457388_image.png)


For our use case, we will need two sets of credentials, one for datajoint database server and the other for github login to clone private repository. Both of these yaml file should be made on at-kubemaster1 as the user will be running it shortly after creating them to create the secrets. **THESE YAML FILES SHOULD NEVER BE UPLOADED GITHUB or ANYWHERE OF THAT MATTER!!!**

DataJoint:

![](https://paper-attachments.dropbox.com/s_807C4A1ACAEC7AEF0E446757A97CF7C3E28D540808B6336A2DC463F7C20352FD_1562807432298_image.png)


After creating that file, use kubectl create -f file_name.yaml to create the secrets.
Upon successful creation of the secret, the user should confirm by using kubectl get secrets

![](https://paper-attachments.dropbox.com/s_807C4A1ACAEC7AEF0E446757A97CF7C3E28D540808B6336A2DC463F7C20352FD_1562807528986_image.png)

# Step 5)

Now we can create the job.yaml file, in this case it is name job_deployment.yaml in the github repository.

![](https://paper-attachments.dropbox.com/s_807C4A1ACAEC7AEF0E446757A97CF7C3E28D540808B6336A2DC463F7C20352FD_1562808127206_image.png)


If the user don’t understand some parts of it, I would recommend the user read through the docs about K8 secrets and commands

https://kubernetes.io/docs/concepts/configuration/secret/

https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/



# Step 6)

For this part, the user can place the yaml file the user created in part 5 in the user's github respo, or just ssh in at-kubemaster1 and make a new yaml file via nano and paste the content over.

After that the user can create the job via kubectl create - f file_name.yaml

![](https://paper-attachments.dropbox.com/s_1658B3DA7264DC308DFF541AD5AF9864461502441102D46F84C863C6F8C40A45_1562585411330_image.png)



# To deploy updates:

Lets say the user have a new version of the user's code the user want to deploy to the cluster. For this the steps are pretty straight forward. All the user need it is to push the new version of the user's code up, delete the current job and relaunch it. The reason why this works is that we setup the pod to clone the repository each time, thus fetching the newest version of the user's code. No need to rebuild the image which takes forever.


# Mounting scratch and stores

For this, we would recommend using hostpath to deal with this. Yes this does assume that every worker node on the cluster have the drive mounting correctly, but they should be via the salt recipe. If they are not please report to the kubernetes channel so the administrators can resolve the issue.

https://kubernetes.io/docs/concepts/storage/volumes/#hostpath

