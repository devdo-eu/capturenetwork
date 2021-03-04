## Neural Network Bot
Inside this folder is bot powered by narrow AI.

`network.json` file contains network architecture details such as number of layers,
 number of neurons in a given layer, layer type, type of activation function, presence of bias and others.
 
`network.md5` file contains all weight for network from json-file.
 
### Network Architecture Details
```
_________________________________________________________________
Layer (type)                 Output Shape              Param #
=================================================================
dense_24 (InputLayer)        [(None, 108)]             0
_________________________________________________________________
dense_25 (Dense)             (None, 64)                6976
_________________________________________________________________
dense_26 (Dense)             (None, 64)                4160
_________________________________________________________________
dense_27 (Dense)             (None, 7)                 455
=================================================================
Total params: 11,591
Trainable params: 11,591
Non-trainable params: 0
```
 
 ### How it was trained?
 This model was trained in unsupervised reinforced fashion. 
 
 What dose it mean? It means that network was learning the game itself by playing

 ### Closing word
 If you had some question - let me know - and I will try to answer.