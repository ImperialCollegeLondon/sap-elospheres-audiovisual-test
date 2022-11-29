### openMHA installation

- Open ubuntu window
- Download and build our fork of openMHA
	**N.B. The SEAT software assumes that tools are in specific places so please follow these instructions carefully **
	
```
	mkdir -p ~/git/alastairhmoore
	cd ~/git/alastairhmoore
	git clone https://github.com/alastairhmoore/openMHA.git
	cd openMHA
	./configure && make -j 4
	make install
```

- Check openmha works

```
	cd ~/git/alastairhmoore/openMHA/
	source bin/thismha.sh
	which mha
	# should be
	# /home/<username>/git/alastairhmoore/openMHA/bin/mha
	cd examples/06-binaural-beamformer
	mha ?read:beamformer.cfg cmd=start cmd=quit
	# should get some text on the screen and a 'beamformer_out.wav' in the current directory
```