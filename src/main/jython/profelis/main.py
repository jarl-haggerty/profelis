"""
This Module is the entry point for Neofelis when used on the desktop.  It parses any command line arguments and if any required arguments
are missing a window is displayed to collect the remaining arguments.  If a directory is specified as the query then that directory and all subdirectories
will be searched for fasta files with a single genome, these files will then be used as queries.  All the arguments are then passed onto the pipeline.
"""

"""
Copyright 2010 Jarl Haggerty

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
       
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from profelis import frame
from java.awt import GraphicsEnvironment

if __name__ == "__main__":
  frame = frame.ProfelisFrame()
  displayMode = GraphicsEnvironment.getLocalGraphicsEnvironment().getDefaultScreenDevice().getDisplayMode()
  frame.setSize(displayMode.getWidth()/2, displayMode.getHeight()/2)
  frame.setLocationRelativeTo(None)
  frame.setVisible(True)

  

  while frame.running:
    pass
  
