---
layout: page
title: "Speed BUMPS"
category: dev
date: 2015-04-22 20:00:00
order: 10
---
### Nightmares Diary

#### Loading time of texture images! asynchronous, late ..
http://stackoverflow.com/questions/7919516/using-textures-in-three-js

```
var texture = materials[i].map;
if(texture instanceof THREE.Texture){
  var image = texture.sourceFile;
}
```

#### Q. How much fast is SmartBody simulation? and when do these calculations occur actually?

- Calculations occur when `SmartBody::SBScene::update()` is called.
- But how much fast are they, remains an open question!

#### Python floating point hell!
http://stackoverflow.com/a/455634/1461232

For some reason Python was continuously throwing runtime errors when trying to print SrVec. The built-in `json.dumps()` is suspected here if it is used by `print`, after using [ujson](https://github.com/esnme/ultrajson) and printing the generated json we got rid of those nasty run-time errors.


#### Pickles security issues
http://www.benfrederickson.com/dont-pickle-your-data/
https://docs.python.org/2/library/pickle.html
http://www.cs.jhu.edu/~s/musings/pickle.html

------

### TODO while wandering around with Brad!

- consider this article about thread safety http://stackoverflow.com/questions/5841896/0mq-how-to-use-zeromq-in-a-threadsafe-manner

- [DZone article about ZMQ](http://java.dzone.com/articles/distributed-systems-zeromq)

- [SOA and ZMQ architecture usecase](http://www.aosabook.org/en/zeromq.html#fig.zeromq.multiuse)

- then: [Getting rid of ZMQ context](http://250bpm.com/blog:23)

- consider using gevent http://blog.pythonisito.com/2011/07/gevent-zeromq-websockets-and-flot-ftw.html

- CONSIDER to use Greenlets!! Seriously!

- CONSIDER (again) throwing this whole Python thing and use NodeJS and benefit from  [SocketIO 1.0](http://socket.io/blog/introducing-socket-io-1-0/#binary)

- [Building a module using NodeJS](https://nodejs.org/api/addons.html)

- WS RFC 6455 links

    ```
    http://en.wikipedia.org/wiki/WebSocket#Browser_support
    http://tools.ietf.org/html/rfc6455#page-5
    http://www.infoq.com/news/2014/06/socketio-1
    ```

