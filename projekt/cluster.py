from pdb import set_trace as T                                                
import numpy as np
                                                                              
import ray                                                                    
from forge.blade.lib.log import BlobSummary

from forge.ethyr.torch import Model                                           
from forge.ethyr.torch.param import getParameters                             

from forge.trinity import Ascend
                                                                              
@ray.remote                                                                   
class Cluster(Ascend):                                                                
   def __init__(self, config, idx, policy):
      super().__init__(config, 0)
      #Train until AGI emerges
      self.model = Model(policy, config)

   def sendModel(self):
      weights = getParameters(self.model.net)
      dones   = [Ascend.send(dest, weights, 'Model')
            for dest in (self.trinity.pantheon, self.trinity.sword)]
      return dones

   def log(self, logs):
      if len(logs) > 0:
         runs, waits = [], []
         for log in logs:
            for k, v in log.items():
               runs.append(v.run)
               waits.append(v.wait)

         run  = np.mean(runs)
         wait = np.mean(waits)
      else:
         run = wait = 0

      return run, wait
 
   def init(self, trinity):
      self.trinity = trinity
      dones = self.sendModel()
      Ascend.get(dones)

      n = self.model.nParams()/1000
      return 'Cluster',  'Initialized {}k Parameter Model'.format(n)

   def step(self):
      grads = self.recv('Gradients')
      grads = [e for e in grads]

      if len(grads) > 0:                                                   
         perf = self.model.step(grads, [], [], 0.0)
         Ascend.send(self.trinity.quill, perf, 'Perf')
         self.sendModel()
