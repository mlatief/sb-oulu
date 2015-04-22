---
layout: page
title: "Changelog"
category: dev
date: 2015-04-22 20:00:00
order: 5
---

#### 2015-04-22

+ `run_crowddemo.py` is successfully running the SmartBody provided `CrowdDemo.py` sample script and observing changing Brads positions and rotations
+ In `sb-cpp/multi_brad_scene` project, successfully managed to run `CrowdDemo.py` script. `multi_brad_scene` is using SmartBody C++ APIs as character animation engine separately from 3D rendering
+ `miniogreSB` renders two ogres created and animated in `ogresmartbody.py` script and rendered using OGRE3D
+ `miniogreSB` project is now runnable from `sb-cpp` solution.
+ Create `gh-pages` branch and write these pages

#### 2015-04-07

+ `brad_scene.py` is successfully managing a SmartBody scene of one brad and listening for `update` and `bml` requests
+ `brad_scene.html` using `threeJS-r69` to render Brad mesh and skeleton converted also using `io_threejs-r69` Blender plugin
+ `brad_socketio.py` using `flask-socketio` extension to handle websockets event from threeJS scene
+ Using ZMQ to route the requests between the socketio loop and SmartBody scene
- Brad in the `brad_scene` doesn't actually move
- Bone-updates aren't glued to threeJS mesh yet!
