### openMHA installation

- Open ubuntu window
- Download fork of openMHA
	**N.B. The SEAT software assumes that tools are in specific places so please use the paths specified **
	
```
	mkdir -p ~/git/alastairhmoore
	cd ~/git/alastairhmoore
	git clone https://github.com/alastairhmoore/openMHA.git
	cd openMHA
```

- Prerequisites can be installed automatically by running the following command. Alternatively, take a look at the script contents and install them manually

```
	bash install_prerequisites_ubuntu.sh
```

- Build openMHA. N.B. The `-j` flag tells make how many CPUs to use. Make this number bigger to build faster.

```
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