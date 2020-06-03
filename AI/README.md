## Neural Network Bot
Inside this folder is bot powered by narrow AI.

`network.json` file contains network architecture details such as number of layers,
 number of neurons in a given layer, layer type, type of activation function, presence of bias and others.
 
`network.md5` file contains all weight for network from json-file.
 
 ### Network Architecture Details
 Neural network of this bot has 4 layers: input(Dense), hidden(Dense), hidden(Dense), output(Dense)
 
 As you can see, all layers are basic `Dense` type.
 
 Input layer has 108 neurons.
 
 Both hidden layers has 54 neurons
 
 Output layer has 7 neurons (one for each move available in game)
 
 So it looks like this: 108 -> 54 -> 54 -> 7
 
 First 3 layers has activation function `sigmoid` and last layer has activation function set to `linear`
 
 It is using float32 variables as weights.
 
 This network use 9241 weights.
 
 ### How it was trained?
 This model was trained in unsupervised reinforced fashion. 
 
 What dose it mean? It means that network was learning the game itself by playing
 
 ### How to run this thing?
 To run this bot you need to install keras, tensorflow and some other dependencies from `requirements.txt` file.
 
 basically if you are using conda you can just type: 
 
 `conda create --name <env> --file requirements.txt`
 
 to create virtual environment with all libraries installed
 
 ### How good it plays the game?
 It plays pretty good. 
 
 I am sure it will take you some time to defeat it.
 
 You should check yourself and try to beat it :)
 
 ### Closing word
 If you can beat this AI bot, I will be happy to hear this story
 
 If you had some question - let me know and I will try to answer.