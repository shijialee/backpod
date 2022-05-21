FROM google/cloud-sdk:alpine

RUN apk add --update --no-cache openjdk8-jre

RUN gcloud components install cloud-firestore-emulator
RUN gcloud components update

RUN gcloud config set project demo-project

CMD gcloud beta emulators firestore start --host-port=0.0.0.0:80
