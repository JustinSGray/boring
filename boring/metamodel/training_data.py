'''
Training data recieved from the COMSOL model

OpenMDAO viewer for the metamodel data. Run the command:
<openmdao view_mm training_data.py -m temp.meta_temp2_data>

Then open a browser and navigate to 
<localhost:5007>

Author: Dustin Hall, Jeff Chin
'''

import numpy as np
import openmdao.api as om
import pickle

## File containing the COMSOL temperature data from xlsx2npy.py script
#t_data = np.load('../util/xlsx2np/outputs/test3.npy')
# t_data2 = np.load('cell2_16_32kj_exra.npy')
# t_data3 = np.load('cell3_16_32kj_exra.npy')
t_data2 = np.load('cell2_v2.npy')
t_data3 = np.load('cell3_v2.npy')

t_data2[t_data2 == 0] = 2400.  # replace broken cases with a (doubly) high value (for ratio calc =2 for invalid cases)
t_data3[t_data3 == 0] = 1200.  # replace broken cases with a high value

# bp = pickle.load( open( "cell2.pickle", "rb" ) )
# print(bp)

# # For loop to pick off the highest temp
# t_max_intermediate = []
# for i in t_data:
#     t_max_intermediate.append(np.max(i, axis=1, keepdims=True))

# # This is passed into the MetaTempGroup class
# t_max_data = np.array(t_max_intermediate)


class MetaTempGroup(om.Group):
    def initialize(self):
        self.options.declare('num_nodes', types=int)

    def setup(self):
        nn = self.options['num_nodes']

        temp2_interp = om.MetaModelStructuredComp(method='scipy_slinear', extrapolate=True)
        temp3_interp = om.MetaModelStructuredComp(method='scipy_slinear', extrapolate=True)


        energy_bp = np.linspace(16.,32.,3)
        extra_bp = np.linspace(1.,2.0,6)
        ratio_bp = np.linspace(0.25,1.0,4)
        #res_bp = np.linspace(0.006, 0.006, 1)

        temp2_interp.add_input('energy', val=16, training_data=energy_bp, units='kJ')         
        temp2_interp.add_input('extra', val=1, training_data=extra_bp, units='mm')
        temp2_interp.add_input('ratio', val=1, training_data=ratio_bp)
        #temp2_interp.add_input('resistance', val=0.006, training_data=res_bp, units='degK*mm**2/W')
        #temp2_interp.add_input('time', val=0, training_data= time_bp, units='s')

        temp3_interp.add_input('energy', val=16, training_data=energy_bp, units='kJ')
        temp3_interp.add_input('extra', val=1, training_data=extra_bp, units='mm')
        temp3_interp.add_input('ratio', val=1, training_data=ratio_bp)
        #temp3_interp.add_input('resistance', val=0.006, training_data=res_bp, units='degK*mm**2/W')

        #temp3_interp.add_input('time', val=0, training_data= time_bp, units='s')
        

        temp2_interp.add_output('temp2_data', val=300*np.ones(nn), training_data=t_data2, units='degK')
        temp3_interp.add_output('temp3_data', val=300*np.ones(nn), training_data=t_data3, units='degK')  # comment out to view_mm


        self.add_subsystem('meta_temp2_data', temp2_interp,
                            promotes_inputs=['energy','extra', 'ratio'],
                            promotes_outputs=['temp2_data'])

        self.add_subsystem('meta_temp3_data', temp3_interp,                               # comment out to view_mm
                            promotes_inputs=['energy','extra', 'ratio'],     # comment out to view_mm
                            promotes_outputs=['temp3_data'])                              # comment out to view_mm


if __name__ == '__main__':
    
    prob = om.Problem()
    nn=1
    mm = prob.model.add_subsystem(name='temp',
                           subsys=MetaTempGroup(num_nodes=nn),
                           promotes_inputs=['energy','extra', 'ratio'],
                           promotes_outputs=['temp2_data','temp3_data'])                 # comment temp3_data out to view_mm


    prob.setup()
    prob.final_setup()