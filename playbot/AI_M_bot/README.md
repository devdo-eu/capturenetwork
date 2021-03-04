## Neural Network Bot
Inside this folder is bot powered by narrow AI.

`network.json` file contains network architecture details such as number of layers,
 number of neurons in a given layer, layer type, type of activation function, presence of bias and others.
 
`network.md5` file contains all weight for network from json-file.

 ### Network Architecture Details
 ```
--------------------------------------------------------------------------------------------------
Layer (type)                    Output Shape         Param #     Connected to
==================================================================================================
A1 (InputLayer)                 [(None, 108)]        0
__________________________________________________________________________________________________
A2 (Dense)                      (None, 64)           6976        A1[0][0]
__________________________________________________________________________________________________
A3 (Dense)                      (None, 64)           4160        A2[0][0]
__________________________________________________________________________________________________
add_45 (Add)                    (None, 64)           0           A2[0][0]
                                                                 A3[0][0]
__________________________________________________________________________________________________
A4 (Dense)                      (None, 64)           4160        add_45[0][0]
__________________________________________________________________________________________________
add_46 (Add)                    (None, 64)           0           A2[0][0]
                                                                 A3[0][0]
                                                                 A4[0][0]
__________________________________________________________________________________________________
A5 (Dense)                      (None, 7)            455         add_46[0][0]
==================================================================================================
Total params: 15,751
Trainable params: 15,751
Non-trainable params: 0
```
 
 ### How it was trained?
 This model was trained in unsupervised reinforced fashion. 
 
 What dose it mean? It means that network was learning the game itself by playing
 
 ### Closing word
 If you had some question - let me know - and I will try to answer.