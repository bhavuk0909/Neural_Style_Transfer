import os
import sys
import scipy.io
import scipy.misc
import matplotlib.pyplot as plt
from matplotlib.pyplot import imshow
from PIL import Image
from nst_utils import *
import numpy as np
import tensorflow as tf
import pprint
%matplotlib inline

pp = pprint.PrettyPrinter(indent=4)
model = load_vgg_model("pretrained-model/imagenet-vgg-verydeep-19.mat")
pp.pprint(model)

content_image = scipy.misc.imread("images/louvre.jpg")
imshow(content_image);

def compute_content_cost(a_C, a_G):
    
    m, n_H, n_W, n_C = a_G.get_shape().as_list()
    
    
    a_C_unrolled = tf.transpose(tf.reshape(a_C, shape=[m, n_H * n_W, n_C]))
    a_G_unrolled = tf.transpose(tf.reshape(a_G, shape=[m, n_H * n_W, n_C]))
    
    
    J_content = 1 / (4*n_H*n_W*n_C)*(tf.reduce_sum(tf.square(tf.subtract(a_C,a_G))))
        
    return J_content

style_image = scipy.misc.imread("images/monet_800600.jpg")
imshow(style_image);


def gram_matrix(A):
    
    
    GA = tf.matmul(A,tf.transpose(A))
    
    
    return GA

def compute_layer_style_cost(a_S, a_G):
    
    m, n_H, n_W, n_C = a_G.get_shape().as_list()
    
    
    a_S = tf.transpose(tf.reshape(a_S,(n_H*n_W,n_C)))
    a_G = tf.transpose(tf.reshape(a_G,(n_H*n_W,n_C)))

    
    GS = gram_matrix(a_S)
    GG = gram_matrix(a_G)

    
    J_style_layer = 1 /(4*n_H*n_W*n_C*n_H*n_W*n_C)*(tf.reduce_sum(tf.square(tf.subtract(GS,GG))))
    
    
    
    return J_style_layer

STYLE_LAYERS = [
    ('conv1_1', 0.2),
    ('conv2_1', 0.2),
    ('conv3_1', 0.2),
    ('conv4_1', 0.2),
    ('conv5_1', 0.2)]

def compute_style_cost(model, STYLE_LAYERS):
    
    J_style = 0

    for layer_name, coeff in STYLE_LAYERS:

        
        out = model[layer_name]

        
        a_S = sess.run(out)

        
        a_G = out
        
        
        J_style_layer = compute_layer_style_cost(a_S, a_G)

        
        J_style += coeff * J_style_layer

    return J_style

def total_cost(J_content, J_style, alpha = 10, beta = 40):
    
    J = alpha*J_content + beta*J_style
    
    
    return J


tf.reset_default_graph()


sess = tf.InteractiveSession()


content_image = scipy.misc.imread("images/louvre_small.jpg")
content_image = reshape_and_normalize_image(content_image)

style_image = scipy.misc.imread("images/monet.jpg")
style_image = reshape_and_normalize_image(style_image)

generated_image = generate_noise_image(content_image)
imshow(generated_image[0]);

model = load_vgg_model("pretrained-model/imagenet-vgg-verydeep-19.mat")

# Assign the content image to be the input of the VGG model.  
sess.run(model['input'].assign(content_image))

# Select the output tensor of layer conv4_2
out = model['conv4_2']

# Set a_C to be the hidden layer activation from the layer we have selected
a_C = sess.run(out)

# Set a_G to be the hidden layer activation from same layer. Here, a_G references model['conv4_2'] 
# and isn't evaluated yet. Later in the code, we'll assign the image G as the model input, so that
# when we run the session, this will be the activations drawn from the appropriate layer, with G as input.
a_G = out

# Compute the content cost
J_content = compute_content_cost(a_C, a_G)

# Assign the input of the model to be the "style" image 
sess.run(model['input'].assign(style_image))

# Compute the style cost
J_style = compute_style_cost(model, STYLE_LAYERS)

J = total_cost(J_content, J_style, alpha = 10, beta = 40)

# define optimizer 
optimizer = tf.train.AdamOptimizer(2.0)

# define train_step 
train_step = optimizer.minimize(J)

def model_nn(sess, input_image, num_iterations = 200):
    
    # Initialize global variables (you need to run the session on the initializer)
    
    sess.run(tf.global_variables_initializer())
    
    
    # Run the noisy input image (initial generated image) through the model. Use assign().
    
    sess.run(model['input'].assign(input_image))
    
    
    for i in range(num_iterations):
    
        # Run the session on the train_step to minimize the total cost
        
        sess.run(train_step)
        
        
        # Compute the generated image by running the session on the current model['input']
        
        generated_image = sess.run(model['input'])
        

        # Print every 20 iteration.
        if i%20 == 0:
            Jt, Jc, Js = sess.run([J, J_content, J_style])
            print("Iteration " + str(i) + " :")
            print("total cost = " + str(Jt))
            print("content cost = " + str(Jc))
            print("style cost = " + str(Js))
            
            # save current generated image in the "/output" directory
            save_image("output/" + str(i) + ".png", generated_image)
    
    # save last generated image
    save_image('output/generated_image.jpg', generated_image)
    
    return generated_image

model_nn(sess, generated_image)
