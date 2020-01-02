#Rotates RGB image into SUV color space. Specular components all in the S channel. U and V channels are purely Lambertian.

from ij import IJ, ImagePlus
from ij.plugin import ImageCalculator
from ij.process import ImageProcessor
from ij.process import FloatProcessor
from org.ejml.simple import SimpleMatrix 
import cmath, math

imp2 = IJ.getImage()
IJ.run("32-bit")
imp2 = IJ.getImage() #need to convert to float before calculations are done


# Import in RGB image as stack with Red slice, Green Slice, Blue Slice
n_slices = imp2.getStack().getSize()
I =[]
for i in range(1, n_slices+1):
  imp2.setSlice(i) 
  n = imp2.getProcessor().getPixels()   
  n2 = [val for val in n]
  I.append(n2)

D= SimpleMatrix(I) # convert RGB list into ejml matrix


# Source color. 111 assumes white light. Calibrate against know light profile of microscope.
s = [[10010, 24306, 23620]] #source color
A = SimpleMatrix(s)#ejml matrix
B= SimpleMatrix.transpose(A.divide(A.normF()))# normalize source

R=SimpleMatrix.transpose(B.svd().getU().negative()) # Rotation matrix from SVD decomposition of source color
c_suv = R.mult(D).getMatrix().data # Rotate RGB


#Fiddly stuff to divide data array into SUV components
L1 = [c_suv[i:i+imp2.height*imp2.width] for i in range(0, len(c_suv), imp2.height*imp2.width)]

# \\J\\, two channel diffuse color vector. See Mallick et al. Beyond Lambert: Reconstructing Specular Surfaces Using Color
J1 =[val*val for val in L1[1]]
J2 =[val*val for val in L1[2]]
J = [math.sqrt(x + y) for x , y in zip(J1, J2)] 

# arrays into images
S = ImagePlus("S", FloatProcessor(imp2.height,imp2.width,L1[0]))
U = ImagePlus("U", FloatProcessor(imp2.height,imp2.width,L1[1]))
V = ImagePlus("V", FloatProcessor(imp2.height,imp2.width,L1[2]))
JNorm = ImagePlus("two channel diffuse color vector", FloatProcessor(imp2.height,imp2.width,J))

#S.show()
#U.show()
#V.show()
JNorm.show()# two channel diffuse color vector show, uncomment for SUV components



