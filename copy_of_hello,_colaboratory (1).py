# -*- coding: utf-8 -*-
"""Copy of Hello, Colaboratory

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1AusQ50TcwbKTUQARLn4ZRpyaVjoDU-MA
"""

import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
import glob
import tensorflow.contrib.slim as slim
# %matplotlib.pyplot inline

x = tf.placeholder(tf.float32, [None, None, None, 4])
y = tf.placeholder(tf.float32, [None, None, None, 4])

def model(inp):
  weights_initializer_stddev = 0.01
  weights_regularized_l2 = 1e-3
  conv1 = tf.layers.conv2d(inp, 3, 5, 1, padding='SAME', activation=tf.nn.relu,
                           kernel_initializer = tf.random_normal_initializer(stddev=weights_initializer_stddev),
                           kernel_regularizer= tf.contrib.layers.l2_regularizer(weights_regularized_l2),
                           name="Conv_1")
  # 144*196
  conv2 = tf.layers.conv2d(conv1, 16, 5, 1,padding='SAME', activation=tf.nn.relu,
                           kernel_initializer = tf.random_normal_initializer(stddev=weights_initializer_stddev),
                           kernel_regularizer= tf.contrib.layers.l2_regularizer(weights_regularized_l2),
                           name="Conv_2")
  covn2 = tf.layers.max_pooling2d(conv2, 2, 2)
  
  # 77*98
  
  conv3 = tf.layers.conv2d(covn2, 32, 3, 1,padding='SAME', activation=tf.nn.relu,
                           kernel_initializer = tf.random_normal_initializer(stddev=weights_initializer_stddev),
                           kernel_regularizer= tf.contrib.layers.l2_regularizer(weights_regularized_l2),
                           name="Conv_3")
  covn3 = tf.layers.max_pooling2d(conv3, 2, 2)
  
  # 37*48
  conv4 = tf.layers.conv2d(covn3, 64, 5, 1,padding='SAME', activation=tf.nn.relu,
                           kernel_initializer = tf.random_normal_initializer(stddev=weights_initializer_stddev),
                           kernel_regularizer= tf.contrib.layers.l2_regularizer(weights_regularized_l2),
                           name="Conv_4")
  covn4= tf.layers.max_pooling2d(conv4, 2, 2)
  conv4 = tf.layers.conv2d(conv4, 128, 5, 1,padding='SAME', activation=tf.nn.relu,
                           kernel_initializer = tf.random_normal_initializer(stddev=weights_initializer_stddev),
                           kernel_regularizer= tf.contrib.layers.l2_regularizer(weights_regularized_l2),
                           name="Conv_5")
  return conv4, conv3, conv2

def deConv_model(last_conv, conv3, conv2):
  weights_initializer_stddev = 0.01
  weights_regularized_l2 = 1e-3
  t_conv1 = tf.layers.conv2d_transpose(last_conv, 128, 1, # kernel_size
                                     padding = 'SAME',
                                     kernel_initializer = tf.random_normal_initializer(stddev=weights_initializer_stddev),
                                     kernel_regularizer= tf.contrib.layers.l2_regularizer(weights_regularized_l2),
                                     name='t_conv1')
  t_conv2 = tf.layers.conv2d_transpose(t_conv1, 64, 5, # kernel_size
                                     padding = 'SAME',strides= (1, 1),
                                     kernel_initializer = tf.random_normal_initializer(stddev=weights_initializer_stddev),
                                     kernel_regularizer= tf.contrib.layers.l2_regularizer(weights_regularized_l2),
                                     name='t_conv2')
  t_conv3 = tf.layers.conv2d_transpose(t_conv2, 32, 3, # kernel_size
                                     padding = 'SAME',strides= (2, 2),
                                     kernel_initializer = tf.random_normal_initializer(stddev=weights_initializer_stddev),
                                     kernel_regularizer= tf.contrib.layers.l2_regularizer(weights_regularized_l2),
                                     name='t_conv3')
  t_conv4 = tf.layers.conv2d_transpose(t_conv3, 16, (2,4), # kernel_size
                                     padding = 'VALID',strides= (2, 2),
                                     kernel_initializer = tf.random_normal_initializer(stddev=weights_initializer_stddev),
                                     kernel_regularizer= tf.contrib.layers.l2_regularizer(weights_regularized_l2),
                                     name='t_conv4')
  t_conv5 = tf.layers.conv2d_transpose(t_conv4, 4, 1, # kernel_size
                                     padding = 'SAME',strides= (1, 1),
                                     kernel_initializer = tf.random_normal_initializer(stddev=weights_initializer_stddev),
                                     kernel_regularizer= tf.contrib.layers.l2_regularizer(weights_regularized_l2),
                                     name='t_conv5')
  return t_conv5, t_conv4, t_conv3, t_conv2

def upsample_and_concat(x1, x2, output_channels, in_channels):

    pool_size = 2
    deconv_filter = tf.Variable(tf.truncated_normal( [pool_size, pool_size, output_channels, in_channels], stddev=0.02))
    deconv = tf.nn.conv2d_transpose(x1, deconv_filter, tf.shape(x2) , strides=[1, pool_size, pool_size, 1] )

    deconv_output =  tf.concat([deconv, x2],3)
    deconv_output.set_shape([None, None, None, output_channels*2])

    return deconv_output

def network(input):   #Unet
    conv1=slim.conv2d(input,32,[3,3], rate=1, activation_fn=lrelu,scope='g_conv1_1')
    conv1=slim.conv2d(conv1,32,[3,3], rate=1, activation_fn=lrelu,scope='g_conv1_2')
    pool1=slim.max_pool2d(conv1, [2, 2], padding='SAME' )

    conv2=slim.conv2d(pool1,64,[3,3], rate=1, activation_fn=lrelu,scope='g_conv2_1')
    conv2=slim.conv2d(conv2,64,[3,3], rate=1, activation_fn=lrelu,scope='g_conv2_2')
    pool2=slim.max_pool2d(conv2, [2, 2], padding='SAME' )

    conv3=slim.conv2d(pool2,128,[3,3], rate=1, activation_fn=lrelu,scope='g_conv3_1')
    conv3=slim.conv2d(conv3,128,[3,3], rate=1, activation_fn=lrelu,scope='g_conv3_2')
    pool3=slim.max_pool2d(conv3, [2, 2], padding='SAME' )

    conv4=slim.conv2d(pool3,256,[3,3], rate=1, activation_fn=lrelu,scope='g_conv4_1')
    conv4=slim.conv2d(conv4,256,[3,3], rate=1, activation_fn=lrelu,scope='g_conv4_2')
    pool4=slim.max_pool2d(conv4, [2, 2], padding='SAME' )

    conv5=slim.conv2d(pool4,512,[3,3], rate=1, activation_fn=lrelu,scope='g_conv5_1')
    conv5=slim.conv2d(conv5,512,[3,3], rate=1, activation_fn=lrelu,scope='g_conv5_2')

    up6 =  upsample_and_concat( conv5, conv4, 256, 512  )
    conv6=slim.conv2d(up6,  256,[3,3], rate=1, activation_fn=lrelu,scope='g_conv6_1')
    conv6=slim.conv2d(conv6,256,[3,3], rate=1, activation_fn=lrelu,scope='g_conv6_2')

    up7 =  upsample_and_concat( conv6, conv3, 128, 256  )
    conv7=slim.conv2d(up7,  128,[3,3], rate=1, activation_fn=lrelu,scope='g_conv7_1')
    conv7=slim.conv2d(conv7,128,[3,3], rate=1, activation_fn=lrelu,scope='g_conv7_2')

    up8 =  upsample_and_concat( conv7, conv2, 64, 128 )
    conv8=slim.conv2d(up8,  64,[3,3], rate=1, activation_fn=lrelu,scope='g_conv8_1')
    conv8=slim.conv2d(conv8,64,[3,3], rate=1, activation_fn=lrelu,scope='g_conv8_2')

    up9 =  upsample_and_concat( conv8, conv1, 32, 64 )
    conv9=slim.conv2d(up9,  32,[3,3], rate=1, activation_fn=lrelu,scope='g_conv9_1')
    conv9=slim.conv2d(conv9,32,[3,3], rate=1, activation_fn=lrelu,scope='g_conv9_2')

    conv10=slim.conv2d(conv9,16,[1,1], rate=1, activation_fn=None, scope='g_conv10')
    out = tf.depth_to_space(conv10,4)
    return out

def lrelu(x):
    return tf.maximum(x*0.2,x)
  
in_image=tf.placeholder(tf.float32,[None,None,None,4])
gt_image=tf.placeholder(tf.float32,[None,None,None,4])

out_image=network(in_image)
sess = tf.Session()

G_loss=tf.reduce_mean(tf.abs(out_image - gt_image))
G_opt=tf.train.AdamOptimizer(learning_rate=0.5).minimize(G_loss)

_,G_current,output=sess.run([G_opt,G_loss,out_image],feed_dict={in_image:imgs_beard,gt_image:imgs_no_beard})

# !wget -O master.zip https://github.com/Keshav-Aggarwal/Beard-Face-Dataset/raw/master/Beard%20Dataset.zip
# !unzip master.zip
# !ls -ltr

l_r = 0.0001
optimizer = tf.train.AdamOptimizer(l_r)

# logits = tf.reshape(,( -1, num_classes), name = "reshape_output")
# correct_label = tf.reshape(y, (-1,num_classes))
def opti(gt, logits):
  """
  This function returns the optimizer for Ground Truth and logits
  """
  logit = tf.reshape(logits,( -1, 4), name = "reshape_output")
  correct_label = tf.reshape(gt, (-1,4))
  print(gt.shape)
  print(logits.shape)
  loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels = correct_label, logits = logit))

  G_opt=tf.train.AdamOptimizer(learning_rate=l_r).minimize(loss)
  return G_opt

beard = glob.glob('beard/*.jpg')
nobeard = glob.glob('no_beard/*.jpg')
imgs_beard = []
imgs_no_beard = []

for path_b, path_n in zip(beard, nobeard):
  imgs_beard.append(plt.imread(path_b))
  imgs_no_beard.append(plt.imread(path_n))

model_str, conv3, conv2 = model(x)
dconv = deConv_model(model_str, conv3, conv2)

imgs_changed = []
with tf.Session() as sess:
  sess.run(tf.global_variables_initializer())
  last_conv = sess.run(model_str, feed_dict={x:imgs_beard})
  t_conv5, t_conv4, t_conv3, t_conv2 = sess.run(dconv, feed_dict={x:imgs_beard})
  optimizer = opti(y, t_conv5)
#   print(t_conv5[0])
#   print("Output is ", y[0])
  sess.run(optimizer, feed_dict = {y: imgs_no_beard})
#   imgs_changed = sess.run(dconv, feed_dict={x:imgs_beard[:2]})
#   print(t_conv5.shape)
#   print(t_conv4.shape)
#   print(t_conv3.shape)
#   print(t_conv2.shape)
#   print(last_conv.shape)

