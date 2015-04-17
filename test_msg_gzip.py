import gzip
import msgpack

with open('test_json.txt', 'rb') as content_file:
    content = content_file.read()
    m_content = msgpack.packb(content)

with gzip.open('test_json.msg.gz', 'wb') as f_out:
    f_out.write(m_content)

with gzip.open('test_json.json.gz', 'wb') as f_out:
    f_out.write(content)
