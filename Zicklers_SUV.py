#Rotates RGB image into SUV color space. Specular components all in the S channel. U and V channels are purely Lambertian.

from ij import IJ, ImagePlus
from ij.plugin import ImageCalculator
from ij.process import ImageProcessor
from ij.process import FloatProcessor
from org.ejml.simple import SimpleMatrix 
import cmath, math

def cart2sph(x,y,z):
    azimuth = math.atan2(y,x)
    elevation = math.atan2(z,math.sqrt(x**2 + y**2))
    r = math.sqrt(x**2 + y**2 + z**2)
    return azimuth, elevation, r


def buildr(psi,dirs):
	R = [[] for i in range(3)]

	N = math.sqrt(dirs[0]+dirs[1]+dirs[2])

	l=dirs[0]/N
	m=dirs[1]/N
	n=dirs[2]/N

	R[0].append(math.cos(psi)+(1-math.cos(psi))*l**2)
	R[0].append(l*m*(1-math.cos(psi))+n*math.sin(psi))
	R[0].append(l*n*(1-math.cos(psi))-m*math.sin(psi))
	R[1].append(l*m*(1-math.cos(psi))-n*math.sin(psi))
	R[1].append(math.cos(psi)+(1-math.cos(psi))*m**2)
	R[1].append(m*n*(1-math.cos(psi))+l*math.sin(psi))
	R[2].append(l*n*(1-math.cos(psi))+m*math.sin(psi))
	R[2].append(m*n*(1-math.cos(psi))-l*math.sin(psi))
	R[2].append(math.cos(psi)+(1-math.cos(psi))*n**2)
	return R
	
	
	
s = [[7532, 8904, 7745]] #source color
A = SimpleMatrix(s)#ejml matrix
B= SimpleMatrix.transpose(A.divide(A.normF())).getMatrix().data# normalize source

c = cart2sph(B[0],B[1],B[2])

#rotationmatrix
R = [val for val in SimpleMatrix(buildr(math.pi/2-c[1], [0,1,0])).mult(SimpleMatrix(buildr(c[0], [0,0,1]))).getMatrix().data]
#rotation same as flipud
Rt = []
ra = [R[i:i+3] for i in range(0, 9, 3)][2]
rb = [R[i:i+3] for i in range(0, 9, 3)][1]
rc = [R[i:i+3] for i in range(0, 9, 3)][0]
Rt.insert(1,ra)
Rt.insert(2,rb)
Rt.insert(3,rc)

Rot = SimpleMatrix(Rt)


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

c_suv = Rot.mult(D).getMatrix().data # Rotate RGB

L1 = [c_suv[i:i+imp2.height*imp2.width] for i in range(0, len(c_suv), imp2.height*imp2.width)]

# \\J\\, two channel diffuse color vector. See Mallick et al. Beyond Lambert: Reconstructing Specular Surfaces Using Color
J1 =[val*val for val in L1[1]]
J2 =[val*val for val in L1[2]]
J = [math.sqrt(x + y) for x , y in zip(J1, J2)] 

# arrays into images
S = ImagePlus("S", FloatProcessor(imp2.width,imp2.height,L1[0]))
U = ImagePlus("U", FloatProcessor(imp2.width,imp2.height,L1[1]))
V = ImagePlus("V", FloatProcessor(imp2.width,imp2.height,L1[2]))
JNorm = ImagePlus("two channel diffuse color vector", FloatProcessor(imp2.width,imp2.height,J))

#S.show()
#U.show()
#V.show()
JNorm.show()# two channel diffuse color vector show, uncomment for SUV components

