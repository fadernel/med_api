FROM python:3.10.13-slim

RUN python -m pip install rasa

WORKDIR /app
COPY ..

RUN rasa train nlu

#set the user to run, don't run as root
USER 1001

# set entrypoint for interactive shells
ENTRYPOINT ["rasa"]

#command to run when container is called to run
CMD ["run", "--enable-api", "--port", "8080"]