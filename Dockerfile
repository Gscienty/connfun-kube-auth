FROM python:3
ADD ./ /workdir
WORKDIR /workdir
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
EXPOSE 5000/tcp
CMD python3 main.py
