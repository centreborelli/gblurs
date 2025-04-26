


def gblur_ymscript(x, s):
	import ymscript
	y = ymscript.gauss(x, s)
	return y

def eprint(*args, **kwargs):
	import sys
	print(*args, file=sys.stderr, **kwargs)

# decorator to quantize an image to 8 bits before appling the filter
# (the output is restored to the original scaling)
def quantize8(f):
	def w(x, *a, **k):
		from numpy import uint8
		m = x.min()
		M = x.max()
		t = (255.0*(x - m)/(M - m)).astype(uint8)
		y = f(t, *a, **k)
		return m + (M - m)*y/255.0
	return w

# decorator to quantize an image to 16 bits before appling the filter
# (the output is restored to the original scaling)
def quantize16(f):
	def w(x, *a, **k):
		from numpy import uint16
		m = x.min()
		M = x.max()
		t = (65535.0*(x - m)/(M - m)).astype(uint16)
		y = f(t, *a, **k)
		return m + (M - m)*y/65535.0
	return w

# decorator to "colorize" functions by treating their first argument channelwise
def colorize(f):
	def w(x, *a, **k):
		if len(x.shape) == 3:
			from numpy import dstack as d
			return d([w(x[:,:,c],*a,**k)for c in range(x.shape[2])])
		assert 2 == len(x.shape)
		return f(x, *a, **k)
	return w


# decorator to add a boundary condition
# b = any valid argument for numpy.pad, for example
# b="constant" (pad by zero)
# b="reflect"
# b="symmetric"
# b="wrap" (periodic)
def boundarize(f):
	def wbo(x, *a, **k):
		if "b" in k:
			b = k["b"]
			del k["b"]
			if not b: return f(x, *a, **k)
			if b == "zero": b = "constant"
			if b == "periodic": b = "wrap"
			from numpy import pad, roll
			if 2 == len(x.shape):
				h,w = x.shape
				X = pad(x, ((0,h),(0,w)), mode=b)
				Y = roll(X, (h//2,w//2), axis=(0,1))
				return wbo(Y, *a, **k)[h//2:h+h//2,w//2:w+w//2]
			if 3 == len(x.shape):
				h,w,d = x.shape
				X = pad(x, ((0,h),(0,w),(0,0)), mode=b)
				Y = roll(X, (h//2,w//2), axis=(0,1))
				return wbo(Y,*a,**k)[h//2:h+h//2,w//2:w+w//2,:]
		return f(x, *a, **k)
	return wbo


@boundarize
@colorize
def gblur_borelli(x, σ):
	# pip install numpy
	from numpy.fft import fft2, ifft2, fftfreq
	from numpy import meshgrid, exp, pi as π
	h,w = x.shape                              # shape of the rectangle
	p,q = meshgrid(fftfreq(w), fftfreq(h))     # build frequency abscissae
	X = fft2(x)                                # move to frequency domain
	F = exp(-2 * π**2 * σ**2 * (p**2 + q**2) ) # filter in frequency domain
	Y = F*X                                    # apply filter
	y = ifft2(Y).real                          # go back to spatial domain
	return y




@quantize8
@boundarize
def gblur_pillow(x, s):
	# pip install pillow
	import numpy, PIL.Image, PIL.ImageFilter
	X = PIL.Image.fromarray(x.squeeze())
	G = PIL.ImageFilter.GaussianBlur(s)
	Y = X.filter(G)
	y = numpy.array(Y).astype(float)
	return y

@boundarize
def gblur_scipy(x, s):
	# pip install scipy
	import scipy.ndimage
	y = scipy.ndimage.gaussian_filter(x, sigma=(s,s,0))
	return y

@boundarize
def gblur_opencv(x, s):
	# pip install opencv-python
	import cv2
	y = cv2.GaussianBlur(x, (0,0), s)
	return y

@boundarize
def gblur_skimage(x, s):
	# pip install scikit-image
	import skimage.filters
	y = skimage.filters.gaussian(x, sigma=s, channel_axis=-1)
	return y

@boundarize
def gblur_torch(x, s):
	# pip install torchvision
	import torchvision.transforms
	n = 2 * round(s * 3) + 1
	T = torchvision.transforms.ToTensor()
	G = torchvision.transforms.GaussianBlur(kernel_size=(n,n), sigma=s)
	y = G(T(x)).numpy().transpose(1,2,0)
	return y

@quantize8
@boundarize
def gblur_imagick(x, s):
	# apt-get install imagemagick
	import tempfile, iio, os
	f = f"{tempfile.NamedTemporaryFile().name}.png"
	c = f"mogrify -gaussian 0x{s} {f}"
	iio.write(f, x)
	os.system(c)
	y = iio.read(f)
	os.system(f"rm {f}")
	return y

#@quantize8
#@boundarize
#def gblur_gmagick(x, s):
	# apt-get install graphicsmagick
#	import tempfile, iio, os
#	f = f"{tempfile.NamedTemporaryFile().name}.png"
#	c = f"gm mogrify -gaussian 0x{s} {f}"
#	iio.write(f, x)
#	os.system(c)
#	y = iio.read(f)
#	return y

# TODO:  fix the kritablur script
@quantize8
@boundarize
def gblur_krita(x, s):
	# apt-get install krita
	import tempfile, iio, os
	from math import pi as π
	from os.path import dirname as d, basename as b
	X = f"{tempfile.NamedTemporaryFile().name}.png"
	Y = f"{tempfile.NamedTemporaryFile().name}.png"
	S = f"{tempfile.NamedTemporaryFile().name}.py"
	c = f"PYTHONPATH={d(S)} kritarunner -s {b(S[:-3])} 2>/dev/null"
	with open(S, "w") as f:
		print(f"""
import krita
app = krita.Krita.instance()
doc = app.openDocument("{X}")
doc.setBatchmode(True)
node = doc.topLevelNodes()[0]
G = app.filter("gaussian blur")
Gc = G.configuration()
Gc.setProperty("horizRadius", {s*π})
Gc.setProperty("vertRadius", {s*π})
G.setConfiguration(Gc)
G.apply(node, 0, 0, doc.width(), doc.height())
doc.exportImage("{Y}", krita.InfoObject())
		""", file=f)
	iio.write(X, x)
	os.system(c)
	y = iio.read(Y)[:,:,0:3]
	os.system(f"rm {X} {Y} {S}")
	return y

## TODO: write an appropriate xmp sidecar to apply, and call darktable-cli
#def gxblur_darktable(x, s):
#	print("fml")
#	exit(43)
#	return x

@boundarize
def gblur_vips(x, s):
	# apt-get install libvips-tools libvips-dev
	# pip install pyvips
	import pyvips
	X = pyvips.Image.new_from_array(x)
	Y = X.gaussblur(s)
	y = Y.numpy()
	return y

@boundarize
def gblur_gmic(x, s):
	# apt-get install gmic
	import tempfile, iio, os
	f = f"{tempfile.NamedTemporaryFile().name}.tiff"
	g = f"{tempfile.NamedTemporaryFile().name}.tiff"
	c = f"gmic {f} -blur {s} -o {g} 2>/dev/null"
	iio.write(f, x)
	os.system(c)
	y = iio.read(g)
	os.system(f"rm {f} {g}")
	return y
	# straightforward version does not work due to pypi shenanigans
	#
	#import gmic  # pip install gmic
	#X = gmic.GmicImage.from_numpy(x)
	#Y = gmic.run(f"blur {s}", X)
	#y = Y.to_numpy()
	#return y

@boundarize
@quantize8
def gblur_ffmpeg(x, s):
	# apt-get install ffmpeg
	import tempfile, iio, os
	f = f"{tempfile.NamedTemporaryFile().name}.png"
	g = f"{tempfile.NamedTemporaryFile().name}.png"
	c = f"ffmpeg -i {f} -filter_complex 'gblur=sigma={s}' {g} 2>/dev/null"
	iio.write(f, x)
	os.system(c)
	y = iio.read(g)
	os.system(f"rm {f} {g}")
	return y

@quantize8
@boundarize
def gblur_gimp(x, s):
	# apt-get install gimp
	import tempfile, iio, os
	from math import pi as π
	s *= π
	X = f"{tempfile.NamedTemporaryFile().name}.png"
	Y = f"{tempfile.NamedTemporaryFile().name}.png"
	c = f"""gimp -i -b "
	  (define img
	    (car (gimp-file-load RUN-NONINTERACTIVE \\\"{X}\\\" \\\"x\\\") )
	  )
	  (define layer
	    (car (gimp-image-get-active-layer img) )
	  )
	  (plug-in-gauss 1 img layer {s} {s} 0)
	  (gimp-file-save RUN-NONINTERACTIVE img layer \\\"{Y}\\\" \\\"y\\\")
	  (gimp-quit 0)
	" 2>/dev/null >/dev/null"""
	iio.write(X, x)
	os.system(c)
	y = iio.read(Y)
	os.system(f"rm {X} {Y}")
	return y

@boundarize
def gblur_julia(x, s):
	# git clone git@github.com:JuliaLang/julia.git
	# make -C julia
	# alias julia=`pwd`/julia/julia
	# julia -e 'using Pkg; Pkg.add("Images")'
	import tempfile, iio, os
	X = f"{tempfile.NamedTemporaryFile().name}.tiff"
	Y = f"{tempfile.NamedTemporaryFile().name}.tiff"
	S = f"{tempfile.NamedTemporaryFile().name}.jl"
	c = f"julia {S}"
	with open(S, "w") as f:
		print(f"""
			using Images
			x = Images.load("{X}")
			k = Kernel.gaussian({s})
			y = imfilter(x, k)
			Images.save("{Y}", y)
		""", file=f)
	iio.write(X, x)
	os.system(c)
	y = iio.read(Y)
	os.system(f"rm {X} {Y} {S}")
	return y

@boundarize
def gblur_octave(x, s):
	# apt-get install octave octave-image
	import tempfile, iio, os
	i = True
	e = "npy" if i else "png"
	r = "iio_read" if i else "imread"
	X = f"{tempfile.NamedTemporaryFile().name}.{e}"
	Y = f"{tempfile.NamedTemporaryFile().name}.{e}"
	S = f"{tempfile.NamedTemporaryFile().name}.m"
	c = f"octave {S}"
	with open(S, "w") as f:
		print(f"""
			pkg load image;
			x = {r}("{X}");
			y = imsmooth(x, "Gaussian", {s});
			{"%" if i else ""}imwrite(y, "{Y}");
			{"" if i else "%"}iio_write("{Y}", y);
		""", file=f)
	iio.write(X, x)
	os.system(c)
	y = iio.read(Y)
	os.system(f"rm {X} {Y} {S}")
	return y

@quantize8
@boundarize
def gblur_imagej(x, s):
	# apt-get install imagej # NOTE: uses legacy, non-fiji version
	import tempfile, iio, os
	i = True
	X = f"{tempfile.NamedTemporaryFile().name}.png"
	Y = f"{tempfile.NamedTemporaryFile().name}.png"
	S = f"{tempfile.NamedTemporaryFile().name}.ijm"
	c = f"imagej -b {S} >/dev/null"
	with open(S, "w") as f:
		print(f"""
			open("{X}");
			run("Gaussian Blur...", "sigma={s}");
			saveAs("Png", "{Y}");
			close();
		""", file=f)
	iio.write(X, x)
	os.system(c)
	y = iio.read(Y)
	os.system(f"rm {X} {Y} {S}")
	return y

@boundarize
@colorize
def gblur_siril(x, s):
	# apt-get install siril
	import tempfile, iio, os
	i = True
	X = f"{tempfile.NamedTemporaryFile().name}.tiff"
	Y = f"{tempfile.NamedTemporaryFile().name}.tiff"
	S = f"{tempfile.NamedTemporaryFile().name}.ssf"
	c = f"siril-cli -s {S} >/dev/null"
	with open(S, "w") as f:
		print(f"""
			requires 1.2.1
			load {X}
			mirrorx
			gauss {s}
			save {Y}
		""", file=f)
	iio.write(X, x)
	os.system(c)
	Y = f"{Y}.fit"
	y = iio.read(Y)
	os.system(f"rm {X} {Y} {S}")
	return y

@quantize8
@boundarize
@colorize
def gblur_netpbm(x, s):
	# apt-get install netpbm
	import tempfile, iio, os
	n = 2 * round(s * 3) + 1
	K = f"{tempfile.NamedTemporaryFile().name}.pam"
	X = f"{tempfile.NamedTemporaryFile().name}.pgm"
	Y = f"{tempfile.NamedTemporaryFile().name}.pgm"
	c1 = f"pamgauss {n} {n} -sigma={s} -maximize > {K}"
	c2 = f"pnmconvol -nooffset -normalize {K} {X} > {Y}"
	iio.write(X, x)
	os.system(c1)
	os.system(c2)
	y = iio.read(Y)
	os.system(f"rm {K} {X} {Y}")
	return y

@boundarize
@colorize
def gblur_mahotas(x, s):
	# pip install mahotas
	import mahotas
	y = mahotas.gaussian_filter(x, s)
	return y

@boundarize
@colorize
def gblur_vigra(x, s):
	# apt-get install python3-vigra
	import vigra
	y = vigra.filters.gaussianSmoothing(x, s)
	return y

@boundarize
@colorize
def gblur_sitk(x, s):
	# pip install SimpleITK
	import SimpleITK
	X = SimpleITK.GetImageFromArray(x)
	Y = SimpleITK.DiscreteGaussian(X, variance=s*s)
	y = SimpleITK.GetArrayFromImage(Y)
	return y

@boundarize
def gblur_cle(x, s):
	# pip install pyclesperanto
	import pyclesperanto
	X = pyclesperanto.push(x)
	Y = pyclesperanto.gaussian_blur(X, sigma_x=0, sigma_y=s, sigma_z=s)
	y = pyclesperanto.pull(Y)
	return y

@boundarize
@colorize
def gblur_arrayfire(x, s):
	# apt-get install python3-arrayfire
	import arrayfire
	import numpy
	n = 2 * round(s * 3) + 1
	K = arrayfire.gaussian_kernel(n, n, s)
	X = arrayfire.from_ndarray(x)
	Y = arrayfire.convolve2(X, K)
	y = numpy.array(Y.to_array()).reshape(x.T.shape).T
	return y


@quantize8
@boundarize
@colorize
def gblur_ipoldct(x, s):
	# pip install ipol
	import ipol
	y = ipol.gauss(x, method="dct", sigma=s)
	return y
@quantize8
@boundarize
@colorize
def gblur_ipoldft(x, s):
	# pip install ipol
	import ipol
	y = ipol.gauss(x, method="dft", sigma=s)
	return y
#@quantize8
#@boundarize
#@colorize
#def gblur_ipolsamp(x, s):
#	# pip install ipol
#	import ipol
#	y = ipol.gauss(x, method="sampled_kernel", sigma=s)
#	return y
#@quantize8
#@boundarize
#@colorize
#def gblur_ipollind(x, s):
#	# pip install ipol
#	import ipol
#	y = ipol.gauss(x, method="lindeberg", sigma=s)
#	return y

#@quantize8
#@boundarize
#@colorize
#def gblur_jimp(x, s):
#       # curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
#       # npm install jimp
#	import tempfile, iio, os
#	i = True
#	X = f"{tempfile.NamedTemporaryFile().name}.png"
#	Y = f"{tempfile.NamedTemporaryFile().name}.png"
#	S = f"{tempfile.NamedTemporaryFile().name}.js"
#	c = f"node {S} {X} {Y}"
#	with open(S, "w") as f:
#		print(f"""
#		const Jimp = require('jimp');
#		Jimp.read('{X}')
#		    .then(image => {{ image.blur({s}) .write('{Y}'); }})
#		    .catch(() => {{}});
#		""", file=f)
#	iio.write(X, x)
#	os.system(c)
#	y = iio.read(Y)
#	os.system(f"rm {X} {Y} {S}")
#	return y


@boundarize
def gblur_tfm(x, s):
	# pip install tensorflow
	# pip install tf-models-official
	if True:
		import logging, os
		os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
		os.environ["GRPC_VERBOSITY"] = "ERROR"
		os.environ["GLOG_minloglevel"] = "2"
		logging.disable(logging.WARNING)
		logging.getLogger("tensorflow").disabled = True

	import tensorflow
	import tensorflow_models
	n = 2 * round(s * 3) + 1
	X = tensorflow.convert_to_tensor(x)
	Y = tensorflow_models.vision.augment.gaussian_filter2d(X, n, s)
	y = Y.numpy()
	return y

@boundarize
def gblur_pix(x, s):
	# pip install dm-pix  # (will install JAX also)
	import dm_pix
	n = 2 * round(s * 3) + 1
	y = dm_pix.gaussian_blur(x, s, n)
	return y

@boundarize
@colorize
def gblur_kornia(x, s):
	# pip install kornia
	import torch
	import kornia.filters
	assert x.ndim == 2
	X = torch.from_numpy(x).unsqueeze(0).unsqueeze(0)  # create 4d array
	X = X.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
	n = 2 * round(s * 3) + 1
	Y = kornia.filters.gaussian_blur2d(X, kernel_size=(n,n), sigma=(s,s))
	y = Y.squeeze().cpu().numpy()
	return y


@boundarize
def gblur_keras(x, s):
	# pip install keras-cv
	if True:
		import logging, os
		os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
		os.environ["GRPC_VERBOSITY"] = "ERROR"
		os.environ["GLOG_minloglevel"] = "2"
		logging.disable(logging.WARNING)
		logging.getLogger("tensorflow").disabled = True
	import tensorflow
	import keras_cv
	n = 2 * round(s * 3) + 1
	G = keras_cv.layers.RandomGaussianBlur(n, (s,s) )  # s=random bounds!
	X = tensorflow.convert_to_tensor(x)
	Y = G(X)
	y = Y.numpy()
	return y

def gblur_pygame(x, s):
	# pip install pygame-ce
	import pygame
	if not pygame.get_init():
		pygame.init()
	X = pygame.surfarray.make_surface(x)
	S = int(s)   # essential, otherwise it breaks
	Y = pygame.transform.gaussian_blur(X, S)
	y = pygame.surfarray.array3d(Y)
	return y

@quantize8
@boundarize
def gblur_rust(x, s):
	# echo do whatever it takes to install the damn rust shit
	import tempfile, iio, os
	X = f"{tempfile.NamedTemporaryFile().name}.png"
	Y = f"{tempfile.NamedTemporaryFile().name}.png"
	c = f"imagecli -i {X} -o {Y} -p 'gaussian {s}'"
	iio.write(X, x)
	os.system(c)
	y = iio.read(Y)
	os.system(f"rm {X} {Y}")
	return y


# visible API
gblurs = [ "borelli", "ymscript", "pillow", "opencv", "skimage",
	   "scipy", "tfm", "keras", "torch", "pygame", "imagick", #"gmagick",
	   "gimp", "krita", "julia", "octave", "gmic", "ffmpeg",
	   "mahotas", "vigra", "sitk", "kornia", "cle", "arrayfire", "imagej",
	   "siril", "netpbm", #"jimp",
	   "ipoldct", "ipoldft", #"ipolsamp", "ipollind",
	   "vips", "pix", "octave", "rust"]

# XXX FIXME MISSING TODO :
#
# * write the darktable wrapper (it is possible, but requires work encoding the
# parameters into a b64 string for darktable:params)
#
# * pnm gaussian blur (mostly of historical interest)
#
# * megawave's fsepconvol
#
# * scilab
#
# * rust:image:blur
# * rust:image:fast_gaussian_blur
# * rust:imageproc:gaussian_blur

# print the install isntructions for all the dependencies
def printinstall():
	L = []
	with open(__file__) as f:
		L = [l.strip() for l in f]
	p = False
	for l in L:
		if l.startswith("def gblur_"):
			p = True
		elif p and l.startswith("# "):
			print(f"RUN {l[2:]}")
		else:
			p = False


# unified interface for all the algorithms above
def G(m, x, σ):
	""" apply a gaussian blur to x of size σ, using method m """
	f = globals()[f"gblur_{m}"]
	return f(x, σ)



# cli interfaces to the above functions
if __name__ == "__main__":
	from sys import argv as v
	def pick_option(o, d):
		if int == type(o): return v[o]
		return type(d)(v[v.index(o)+1]) if o in v else d
	if len(v) < 2 or v[1] not in gblurs:
		print(f"usage:\n\tgblurs {{{'|'.join(gblurs)}}}")
		exit(0)
	import iio
	i = pick_option("-i", "-")
	o = pick_option("-o", "-")
	s = pick_option("-s", 3.0)
	b = pick_option("-b", "")
	f = globals()[f"gblur_{v[1]}"]
	x = iio.read(i)
	if b:
		y = f(x, s, b=b)
	else:
		y = f(x, s)
	iio.write(o, y)

version = 8
