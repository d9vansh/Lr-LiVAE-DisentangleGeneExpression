from ops import *
import tensorflow as tf
import tensorflow.keras.layers as tkl

def VGG16(inputs, out_dim, keep_prob = 0.5, is_training = True, isvae = False, size = 64):
    with tf.name_scope('conv1_1') as scope:
        out = tkl.Conv2D(inputs, num_outputs=64, kernel_size=3, stride=1, activation=tf.nn.relu,
                         normalizer=tkl.BatchNormalization,
                         normalizer_params={'scale': True, 'is_training':is_training})
    with tf.name_scope('conv1_2') as scope:
        out = tkl.Conv2D(out, num_outputs=64, kernel_size=3, stride=1, activation=tf.nn.relu,
                         normalizer=tkl.BatchNormalization,
                         normalizer_params={'scale': True, 'is_training': is_training})
    out = tkl.MaxPool2D(out, kernel_size=2, stride=2)

    with tf.name_scope('conv2_1') as scope:
        out = tkl.Conv2D(out, num_outputs=128, kernel_size=3, stride=1, activation=tf.nn.relu,
                         normalizer=tkl.BatchNormalization,
                         normalizer_params={'scale': True, 'is_training': is_training})
    with tf.name_scope('conv2_2') as scope:
        out = tkl.Conv2D(out, num_outputs=128, kernel_size=3, stride=1, activation=tf.nn.relu,
                         normalizer=tkl.BatchNormalization,
                         normalizer_params={'scale': True, 'is_training': is_training})
    out = tkl.MaxPool2D(out, kernel_size=2, stride=2)

    with tf.name_scope('conv3_1') as scope:
        out = tkl.Conv2D(out, num_outputs=256, kernel_size=3, stride=1, activation=tf.nn.relu,
                         normalizer=tkl.BatchNormalization,
                         normalizer_params={'scale': True, 'is_training': is_training})
    with tf.name_scope('conv3_2') as scope:
        out = tkl.Conv2D(out, num_outputs=256, kernel_size=3, stride=1, activation=tf.nn.relu,
                         normalizer=tkl.BatchNormalization,
                         normalizer_params={'scale': True, 'is_training': is_training})
    with tf.name_scope('conv3_3') as scope:
        out = tkl.Conv2D(out, num_outputs=256, kernel_size=3, stride=1, activation=tf.nn.relu,
                         normalizer=tkl.BatchNormalization,
                         normalizer_params={'scale': True, 'is_training': is_training})
    out = tkl.MaxPool2D(out, kernel_size=2, stride=2)

    with tf.name_scope('conv4_1') as scope:
        out = tkl.Conv2D(out, num_outputs=512, kernel_size=3, stride=1, activation=tf.nn.relu,
                         normalizer=tkl.BatchNormalization,
                         normalizer_params={'scale': True, 'is_training': is_training})
    with tf.name_scope('conv4_2') as scope:
        out = tkl.Conv2D(out, num_outputs=512, kernel_size=3, stride=1, activation=tf.nn.relu,
                         normalizer=tkl.BatchNormalization,
                         normalizer_params={'scale': True, 'is_training': is_training})
    with tf.name_scope('conv4_3') as scope:
        out = tkl.Conv2D(out, num_outputs=512, kernel_size=3, stride=1, activation=tf.nn.relu,
                         normalizer=tkl.BatchNormalization,
                         normalizer_params={'scale': True, 'is_training': is_training})
    out = tkl.MaxPool2D(out, kernel_size=2, stride=2)

    with tf.name_scope('conv5_1') as scope:
        out = tkl.Conv2D(out, num_outputs=512, kernel_size=3, stride=1, activation=tf.nn.relu,
                         normalizer=tkl.BatchNormalization,
                         normalizer_params={'scale': True, 'is_training': is_training})
    with tf.name_scope('conv5_2') as scope:
        out = tkl.Conv2D(out, num_outputs=512, kernel_size=3, stride=1, activation=tf.nn.relu,
                         normalizer=tkl.BatchNormalization,
                         normalizer_params={'scale': True, 'is_training': is_training})
    with tf.name_scope('conv5_3') as scope:
        out = tkl.Conv2D(out, num_outputs=512, kernel_size=3, stride=1, activation=tf.nn.relu,
                         normalizer=tkl.BatchNormalization,
                         normalizer_params={'scale': True, 'is_training': is_training})
    # out = tkl.MaxPool2D(out, kernel_size=2, stride=2)

    out = tkl.AveragePooling2D(out, kernel_size= size/(2**5), stride=size/(2**5))

    out = tkl.Flatten(out)

    with tf.name_scope('fc6') as scope:
        out = tkl.Dense(1024, activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                  normalizer_params={'scale': True, trainable=True})(out)

    if isvae:
        with tf.name_scope('fc8') as scope:
            out1 = tkl.Dense(out_dim, activation=None)(out)
            out2 = tkl.Dense(out_dim, activation=None)(out)
        return out1, out2

    else:
        with tf.name_scope('fc8') as scope:
            out = tkl.Dense(out_dim, activation=None)(out)

        return out

class IdentityFace(object):
    def __init__(self, y_dim = 530, z_dim = 256, size = 64):
        self.name = 'IdentityFace'
        self.z_dim = z_dim
        self.y_dim = y_dim
        self.size = size

    def __call__(self, inputs, is_training = True, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            with tf.variable_scope('base_layers'):
                out = VGG16(inputs, self.z_dim, is_training = is_training, size = self.size)

            with tf.variable_scope('mean_var'):
                mean_c = tf.get_variable('centers_c', [self.y_dim, self.z_dim], dtype=tf.float32,
                                          initializer=tf.contrib.layers.xavier_initializer())
                variance_c_var = tf.get_variable('variance_c', [self.y_dim, self.z_dim], dtype=tf.float32,
                                               initializer=tf.constant_initializer(0.54))
                variance_c = tf.nn.softplus(variance_c_var)


            return out, mean_c, variance_c_var, variance_c

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

    @property
    def mean_var_vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name + '/mean_var')

    @property
    def mu_logvar_vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name + '/mu_logvar')

    @property
    def base_layers_vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name + '/base_layers')

class AttributeFace(object):
    def __init__(self, z_dim = 256, size =64):
        self.name = 'AttributeFace'
        self.z_dim = z_dim
        self.size = size

    def __call__(self, inputs, is_training = True, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            z_mu, z_logvar = VGG16(inputs, self.z_dim, is_training = is_training, isvae = True, size = self.size)
            return z_mu, z_logvar

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

class LatentDiscriminator(object):
    def __init__(self, y_dim = 530):
        self.name = 'LatentDiscriminator'
        self.y_dim = y_dim

    def __call__(self, inputs, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            out = tkl.Dense(256, activation=tf.nn.relu)(inputs)
            out = tkl.Dense(self.y_dim, activation=None)(out)
            return out
    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

class EncoderFace(object):
    def __init__(self, z_dim = 512, size =128):
        self.name = 'AttributeMnist'
        self.z_dim = z_dim
        self.size = size

    def __call__(self, inputs, y, is_training = True, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            y_shapes = y.get_shape().as_list()
            x_shapes = inputs.get_shape().as_list()
            y = tf.reshape(y, [-1, 1, 1, y_shapes[1]])

            x = tf.concat([inputs, tf.tile(y,[1, x_shapes[1], x_shapes[2], 1])], axis = 3)

            z_mu, z_logvar = VGG16(x, self.z_dim, is_training=is_training, isvae=True, size=self.size)

            return z_mu, z_logvar

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)


class GeneratorFace(object):
    def __init__(self, size = 128):
        self.name = 'GeneratorFace'
        self.size = size

    def __call__(self, z_c, z_p, is_training = True, reuse = False):
        # 2 fully-connected layers, followed by 6 deconv layers with 2-by-2 upsampling
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            z = tf.concat([z_c, z_p], axis = 1)

            w = self.size / (2 ** 5)

            with tf.name_scope('fc8') as scope:
                out = tkl.Dense(1024, activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                          normalizer_params={'scale': True, trainable=True})(z)
            with tf.name_scope('fc6') as scope:
                out = tkl.Dense(w*w*512, activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                          normalizer_params={'scale': True, 'is_training': is_training})(out)
            out = tf.reshape(out, (-1, w, w, 512))

            with tf.name_scope('conv5_3') as scope:
                out = tkl.Conv2DTranspose(out, num_outputs=512, kernel_size=3, stride=2, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})
            with tf.name_scope('conv5_2') as scope:
                out = tkl.Conv2DTranspose(out, num_outputs=512, kernel_size=3, stride=1, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})
            with tf.name_scope('conv5_1') as scope:
                out = tkl.Conv2DTranspose(out, num_outputs=512, kernel_size=3, stride=1, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})
            with tf.name_scope('conv4_3') as scope:
                out = tkl.Conv2DTranspose(out, num_outputs=512, kernel_size=3, stride=2, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})
            with tf.name_scope('conv4_2') as scope:
                out = tkl.Conv2DTranspose(out, num_outputs=512, kernel_size=3, stride=1, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})
            with tf.name_scope('conv4_1') as scope:
                out = tkl.Conv2DTranspose(out, num_outputs=256, kernel_size=3, stride=1, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})
            with tf.name_scope('conv3_3') as scope:
                out = tkl.Conv2DTranspose(out, num_outputs=256, kernel_size=3, stride=2, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})
            with tf.name_scope('conv3_2') as scope:
                out = tkl.Conv2DTranspose(out, num_outputs=256, kernel_size=3, stride=1, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})
            with tf.name_scope('conv3_1') as scope:
                out = tkl.Conv2DTranspose(out, num_outputs=128, kernel_size=3, stride=1, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})
            with tf.name_scope('conv2_2') as scope:
                out = tkl.Conv2DTranspose(out, num_outputs=128, kernel_size=3, stride=2, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})
            with tf.name_scope('conv2_1') as scope:
                out = tkl.Conv2DTranspose(out, num_outputs=64, kernel_size=3, stride=1, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})
            with tf.name_scope('conv1_2') as scope:
                out = tkl.Conv2DTranspose(out, num_outputs=64, kernel_size=3, stride=2, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})
            with tf.name_scope('conv1_1') as scope:
                out = tkl.Conv2DTranspose(out, num_outputs=3, kernel_size=3, stride=1, activation=tf.nn.tanh)

            return out

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

# class GeneratorFaceConditionalBN(object):
#     def __init__(self, size, category):
#         self.name = 'GeneratorFaceConditionalBN'
#         self.size = size
#         self.category = category
#
#     def __call__(self, labels, z, is_training = True, reuse = False, alpha=1.0):
#         # labels: shape is [batch_size, 1]. value is in category.
#         # 2 fully-connected layers, followed by 6 deconv layers with 2-by-2 upsampling
#         with tf.variable_scope(self.name) as scope:
#             if reuse:
#                 scope.reuse_variables()
#
#             w = self.size / (2 ** 5)
#
#             out = Dense(z, 1024, use_bias=False, sn=False, scope='fc8')
#             bn8 = ConditionalBatchNormalization(self.category)
#             out = tf.nn.relu(bn8(out, labels=labels, training = is_training))
#
#             out = Dense(out,  w*w*512, use_bias=False, sn=False, scope='fc6')
#             bn6 = ConditionalBatchNormalization(self.category)
#             out = tf.nn.relu(bn6(out, labels=labels, training = is_training))
#
#             out = tf.reshape(out, (-1, w, w, 512))
#
#             with tf.name_scope('conv5_3') as scope:
#                 out = tkl.Conv2DTranspose(out, num_outputs=512, kernel_size=3, stride=2, activation=None, biases_initializer = None)
#                 bn5_3 = ConditionalBatchNormalization(self.category)
#                 out = tf.nn.relu(bn5_3(out, labels=labels, training = is_training))
#
#             with tf.name_scope('conv5_2') as scope:
#                 out = tkl.Conv2DTranspose(out, num_outputs=512, kernel_size=3, stride=1, activation=None, biases_initializer = None)
#                 bn5_2 = ConditionalBatchNormalization(self.category)
#                 out = tf.nn.relu(bn5_2(out, labels=labels, training=is_training))
#
#             with tf.name_scope('conv5_1') as scope:
#                 out = tkl.Conv2DTranspose(out, num_outputs=512, kernel_size=3, stride=1, activation=None, biases_initializer = None)
#                 bn5_1 = ConditionalBatchNormalization(self.category)
#                 out = tf.nn.relu(bn5_1(out, labels=labels, training=is_training))
#
#             with tf.name_scope('conv4_3') as scope:
#                 out = tkl.Conv2DTranspose(out, num_outputs=512, kernel_size=3, stride=2, activation=None, biases_initializer = None)
#                 bn4_3 = ConditionalBatchNormalization(self.category)
#                 out = tf.nn.relu(bn4_3(out, labels=labels, training=is_training))
#
#             with tf.name_scope('conv4_2') as scope:
#                 out = tkl.Conv2DTranspose(out, num_outputs=512, kernel_size=3, stride=1, activation=None, biases_initializer = None)
#                 bn4_2 = ConditionalBatchNormalization(self.category)
#                 out = tf.nn.relu(bn4_2(out, labels=labels, training=is_training))
#
#             with tf.name_scope('conv4_1') as scope:
#                 out = tkl.Conv2DTranspose(out, num_outputs=256, kernel_size=3, stride=1, activation=None, biases_initializer = None)
#                 bn4_1 = ConditionalBatchNormalization(self.category)
#                 out = tf.nn.relu(bn4_1(out, labels=labels, training=is_training))
#
#             with tf.name_scope('conv3_3') as scope:
#                 out = tkl.Conv2DTranspose(out, num_outputs=256, kernel_size=3, stride=2, activation=None, biases_initializer = None)
#                 bn3_3 = ConditionalBatchNormalization(self.category)
#                 out = tf.nn.relu(bn3_3(out, labels=labels, training=is_training))
#
#             with tf.name_scope('conv3_2') as scope:
#                 out = tkl.Conv2DTranspose(out, num_outputs=256, kernel_size=3, stride=1, activation=None, biases_initializer = None)
#                 bn3_2 = ConditionalBatchNormalization(self.category)
#                 out = tf.nn.relu(bn3_2(out, labels=labels, training=is_training))
#
#             with tf.name_scope('conv3_1') as scope:
#                 out = tkl.Conv2DTranspose(out, num_outputs=128, kernel_size=3, stride=1, activation=None, biases_initializer = None)
#                 bn3_1 = ConditionalBatchNormalization(self.category)
#                 out = tf.nn.relu(bn3_1(out, labels=labels, training=is_training))
#
#             with tf.name_scope('conv2_2') as scope:
#                 out = tkl.Conv2DTranspose(out, num_outputs=128, kernel_size=3, stride=2, activation=None, biases_initializer = None)
#                 bn2_2 = ConditionalBatchNormalization(self.category)
#                 out = tf.nn.relu(bn2_2(out, labels=labels, training=is_training))
#
#             with tf.name_scope('conv2_1') as scope:
#                 out = tkl.Conv2DTranspose(out, num_outputs=64, kernel_size=3, stride=1, activation=None, biases_initializer = None)
#                 bn2_1 = ConditionalBatchNormalization(self.category)
#                 out = tf.nn.relu(bn2_1(out, labels=labels, training=is_training))
#
#             with tf.name_scope('conv1_2') as scope:
#                 out = tkl.Conv2DTranspose(out, num_outputs=64, kernel_size=3, stride=2, activation=None, biases_initializer = None)
#                 bn1_2 = ConditionalBatchNormalization(self.category)
#                 out = tf.nn.relu(bn1_2(out, labels=labels, training=is_training))
#
#             with tf.name_scope('conv1_1') as scope:
#                 out = tkl.Conv2DTranspose(out, num_outputs=3, kernel_size=3, stride=1, activation=tf.nn.tanh)
#
#             return out
#
#     @property
#     def vars(self):
#         return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

class DiscriminatorFace(object):
    def __init__(self, z_dim = 256, size = 64):
        self.name = 'DiscriminatorFace'
        self.z_dim = z_dim
        self.size = size

    def __call__(self, inputs, is_training = True, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            out = tkl.Conv2D(inputs, num_outputs=64, kernel_size=3, stride=2, activation=lrelu)
            out = tkl.Conv2D(out, num_outputs=128, kernel_size=3, stride=2, activation=lrelu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})
            out = tkl.Conv2D(out, num_outputs=256, kernel_size=3, stride=1, activation=lrelu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})
            out = tkl.Conv2D(out, num_outputs=256, kernel_size=3, stride=2, activation=lrelu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})
            out = tkl.Conv2D(out, num_outputs=512, kernel_size=3, stride=1, activation=lrelu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})
            out = tkl.Conv2D(out, num_outputs=512, kernel_size=3, stride=2, activation=lrelu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})
            out = tkl.Conv2D(out, num_outputs=512, kernel_size=3, stride=2, activation=lrelu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})

            out = tkl.AveragePooling2D(out, kernel_size=self.size / (2**5), stride=self.size / (2**5))
            out = tkl.Flatten(out)
            out = tkl.Dense(out, 1024, activation=lrelu, normalizer=tkl.BatchNormalization,
                                      normalizer_params={'scale': True, 'is_training': is_training})

            d = tkl.Dense(out, 1, activation=None)

            q = tkl.Dense(out, 1024, activation=lrelu, normalizer=tkl.BatchNormalization,
                                      normalizer_params={'scale': True, 'is_training': is_training})

            q = tkl.Dense(q, self.z_dim, activation=None)

            return d, q, out

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

class DiscriminatorFaceSN(object):
    def __init__(self, size = 64):
        self.name = 'DiscriminatorFaceSN'
        self.size = size

    def __call__(self, inputs, y, is_training = True, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()

            out = lrelu(conv(inputs, channels=64, kernel=3, stride=2, pad=1, sn=True, scope='conv_1'))

            out = lrelu(conv(out, channels=128, kernel=3, stride=2, pad=1, sn=True, scope='conv_2'))

            out = lrelu(conv(out, channels=256, kernel=3, stride=1, pad=1, sn=True, scope='conv_3'))

            out = lrelu(conv(out, channels=256, kernel=3, stride=2, pad=1, sn=True, scope='conv_4'))

            out = lrelu(conv(out, channels=512, kernel=3, stride=1, pad=1, sn=True, scope='conv_5'))

            out = lrelu(conv(out, channels=512, kernel=3, stride=2, pad=1, sn=True, scope='conv_6'))

            out = lrelu(conv(out, channels=512, kernel=3, stride=2, pad=1, sn=True, scope='conv_7'))

            out = tkl.AveragePooling2D(out, kernel_size=self.size / (2**5), stride=self.size / (2**5))
            out = tkl.Flatten(out)

            out = lrelu(Dense(out, 1024, sn=True, scope='fc_8'))

            y_proj = Dense(y, 1024, use_bias=False, sn=True, scope='y_proj')
            y_proj = tf.reduce_sum(y_proj * out, axis=1, keep_dims=True)

            d = Dense(out, 1, sn=True, scope='fc_9')
            return d + y_proj

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)



### MNIST FASHION MNIST

class IdentityMnist(object):
    def __init__(self, y_dim = 10, z_dim = 100, size = 28, isrefine = False):
        self.name = 'IdentityMnist'
        self.z_dim = z_dim
        self.y_dim = y_dim
        self.size = size
        self.isrefine = isrefine

    def __call__(self, inputs, is_training = True, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            with tf.variable_scope('base_layers'):
                out = tkl.Conv2D(inputs, num_outputs=64, kernel_size=5, stride=2, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})
                out = tkl.Conv2D(out, num_outputs=128, kernel_size=5, stride=2, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})

                out = tkl.Conv2D(out, num_outputs=256, kernel_size=5, stride=2, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})

                out = tkl.Flatten(out)

                out = tkl.Dense(out, 1024, activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                          normalizer_params={'scale': True, 'is_training': is_training})

                out = tkl.Dense(out, self.z_dim, activation=None)


            with tf.variable_scope('mean_var'):
                mean_c = tf.get_variable('centers_c', [self.y_dim, self.z_dim], dtype=tf.float32,
                                          initializer=tf.contrib.layers.xavier_initializer())
                variance_c_var = tf.get_variable('variance_c', [self.y_dim, self.z_dim], dtype=tf.float32,
                                               initializer=tf.constant_initializer(0.54))
                variance_c = tf.nn.softplus(variance_c_var)
            if self.isrefine:
                with tf.variable_scope('mu_logvar'):
                    mu = tkl.Dense(out, self.z_dim, activation=None)
                    logvar = tkl.Dense(out, self.z_dim, activation=None)
                return out, mean_c, variance_c, mu, logvar
            else:
                return out, mean_c, variance_c_var, variance_c

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

    @property
    def mean_var_vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name + '/mean_var')

    @property
    def mu_logvar_vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name + '/mu_logvar')

    @property
    def base_layers_vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name + '/base_layers')

class IdentityMnist_fixsigma(object):
    def __init__(self, y_dim = 10, z_dim = 100, size = 28):
        self.name = 'IdentityMnist'
        self.z_dim = z_dim
        self.y_dim = y_dim
        self.size = size

    def __call__(self, inputs, is_training = True, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            with tf.variable_scope('base_layers'):
                out = tkl.Conv2D(inputs, num_outputs=64, kernel_size=5, stride=2, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})
                out = tkl.Conv2D(out, num_outputs=128, kernel_size=5, stride=2, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})

                out = tkl.Conv2D(out, num_outputs=256, kernel_size=5, stride=2, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})

                out = tkl.Flatten(out)

                out = tkl.Dense(out, 1024, activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                          normalizer_params={'scale': True, 'is_training': is_training})

                out = tkl.Dense(out, self.z_dim, activation=None)


            with tf.variable_scope('mean_var'):
                mean_c = tf.get_variable('centers_c', [self.y_dim, self.z_dim], dtype=tf.float32,
                                          initializer=tf.contrib.layers.xavier_initializer())
                variance_c = tf.get_variable('variance_c', [self.y_dim, self.z_dim], dtype=tf.float32,
                                               initializer=tf.constant_initializer(0.25), trainable=False)

            return out, mean_c, variance_c

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

    @property
    def mean_var_vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name + '/mean_var')

    @property
    def base_layers_vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name + '/base_layers')


class AttributeMnist(object):
    def __init__(self, z_dim = 100, size =28):
        self.name = 'AttributeMnist'
        self.z_dim = z_dim
        self.size = size

    def __call__(self, inputs, is_training = True, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            out = tkl.Conv2D(inputs, num_outputs=64, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})
            out = tkl.Conv2D(out, num_outputs=128, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})

            out = tkl.Conv2D(out, num_outputs=256, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})

            out = tkl.Flatten(out)

            out = tkl.Dense(out, 1024, activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                      normalizer_params={'scale': True, 'is_training': is_training})

            z_mu = tkl.Dense(out, self.z_dim, activation=None)

            z_logvar = tkl.Dense(out, self.z_dim, activation=None)

            return z_mu, z_logvar

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

class EncoderMnist(object):
    def __init__(self, z_dim = 100, size =28):
        self.name = 'AttributeMnist'
        self.z_dim = z_dim
        self.size = size

    def __call__(self, inputs, y, is_training = True, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            y_shapes = y.get_shape().as_list()
            x_shapes = inputs.get_shape().as_list()
            y = tf.reshape(y, [-1, 1, 1, y_shapes[1]])

            x = tf.concat([inputs, tf.tile(y,[1, x_shapes[1], x_shapes[2], 1])], axis = 3)

            out = tkl.Conv2D(x, num_outputs=64, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})
            out = tkl.Conv2D(out, num_outputs=128, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})

            out = tkl.Conv2D(out, num_outputs=256, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})

            out = tkl.Flatten(out)

            out = tkl.Dense(out, 1024, activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                      normalizer_params={'scale': True, 'is_training': is_training})

            z_mu = tkl.Dense(out, self.z_dim, activation=None)

            z_logvar = tkl.Dense(out, self.z_dim, activation=None)

            return z_mu, z_logvar

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)


class GeneratorMnist(object):
    def __init__(self, size = 28, is_color = False):
        self.name = 'GeneratorMnist'
        self.size = size
        self.is_color = is_color

    def __call__(self, z_c, z_p, is_training = True, reuse = False):
        # 2 fully-connected layers, followed by 6 deconv layers with 2-by-2 upsampling
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            z = tf.concat([z_c, z_p], axis = 1)

            g = tkl.Dense(z, 2*2*256, activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                    normalizer_params={'scale': True, 'is_training': is_training})
            g = tf.reshape(g, (-1, 2, 2, 256))  # 2x2x256

            g = tkl.Conv2DTranspose(g, 256, 5, stride=2,  # 7x7x128
                                     activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                     normalizer_params={'scale': True, 'is_training': is_training}, padding='VALID')

            g = tkl.Conv2DTranspose(g, 128, 5, stride=2,  # 14x14x64
                                     activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                     normalizer_params={'scale': True, 'is_training': is_training}, padding='SAME')

            g = tkl.Conv2DTranspose(g, 32, 5, stride=2,  # 14x14x64
                                     activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                     normalizer_params={'scale': True, 'is_training': is_training}, padding='SAME')

            if self.is_color:
                g = tkl.Conv2DTranspose(g, 3, 5, stride=1,  # 28x28x3
                                         activation=tf.nn.tanh, padding='SAME')
            else:
                g = tkl.Conv2DTranspose(g, 1, 5, stride=1,  # 28x28x1
                                         activation=tf.nn.tanh, padding='SAME')
            return g

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

class ClassifierMnist(object):
    def __init__(self, y_dim = 530, z_dim = 256, size = 64):
        self.name = 'IdentityMnist'
        self.z_dim = z_dim
        self.y_dim = y_dim
        self.size = size

    def __call__(self, inputs, is_training = True, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            out = tkl.Conv2D(inputs, num_outputs=64, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})
            out = tkl.Conv2D(out, num_outputs=128, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})

            out = tkl.Conv2D(out, num_outputs=256, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})

            out = tkl.Flatten(out)

            out = tkl.Dense(out, 2048, activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                      normalizer_params={'scale': True, 'is_training': is_training})

            out = tkl.Dense(out, self.z_dim, activation=None)

            with tf.variable_scope('mean_var'):
                mean_c = tf.get_variable('centers_c', [self.y_dim, self.z_dim], dtype=tf.float32,
                                         initializer=tf.contrib.layers.xavier_initializer())
                variance_c = tf.get_variable('variance_c', [self.y_dim, self.z_dim], dtype=tf.float32,
                                             initializer=tf.constant_initializer(1))
            return out, mean_c, variance_c

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

    @property
    def mean_var_vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name + '/mean_var')

class DiscriminatorMnistSN(object):
    def __init__(self, z_dim = 100, size = 28):
        self.name = 'DiscriminatorMnistSN'
        self.z_dim = z_dim
        self.size = size

    def __call__(self, inputs, y, is_training = True, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()

            out = lrelu(conv(inputs, channels=32, kernel=5, stride=1, pad=2, sn=True, scope='conv_1'))

            out = lrelu(conv(out, channels=128, kernel=5, stride=2, pad=2, sn=True, scope='conv_2'))

            out = lrelu(conv(out, channels=256, kernel=5, stride=2, pad=2, sn=True, scope='conv_3'))

            out = lrelu(conv(out, channels=256, kernel=5, stride=2, pad=2, sn=True, scope='conv_4'))

            out = tkl.Flatten(out)

            out = lrelu(Dense(out, 512, sn=True, scope='fc_8'))

            y_proj = Dense(y, 512, use_bias=False, sn=True, scope='y_proj')
            y_proj = tf.reduce_sum(y_proj * out, axis=1, keep_dims=True)

            d = Dense(out, 1, sn=True, scope='fc_9')
            return d + y_proj
    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

class DiscriminatorMnistSNComb(object):
    def __init__(self, z_dim = 100, size = 28):
        self.name = 'DiscriminatorMnistSNComb'
        self.z_dim = z_dim
        self.size = size

    def __call__(self, inputs, is_training = True, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()

            out = lrelu(conv(inputs, channels=32, kernel=5, stride=1, pad=2, sn=True, scope='conv_1'))

            out = lrelu(conv(out, channels=128, kernel=5, stride=2, pad=2, sn=True, scope='conv_2'))

            out = lrelu(conv(out, channels=256, kernel=5, stride=2, pad=2, sn=True, scope='conv_3'))

            out = lrelu(conv(out, channels=256, kernel=5, stride=2, pad=2, sn=True, scope='conv_4'))

            out = tkl.Flatten(out)

            out = lrelu(Dense(out, 512, sn=True, scope='fc_8'))

            d = Dense(out, 1, sn=True, scope='fc_9')
            return d
    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

#### SVHN
class GeneratorSVHN(object):
    def __init__(self, size = 32):
        self.name = 'GeneratorSVHN'
        self.size = size

    def __call__(self, z_c, z_p, is_training = True, reuse = False):
        # 2 fully-connected layers, followed by 6 deconv layers with 2-by-2 upsampling
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            z = tf.concat([z_c, z_p], axis = 1)

            g = tkl.Dense(z, 2*2*256, activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                    normalizer_params={'scale': True, 'is_training': is_training})
            g = tf.reshape(g, (-1, 2, 2, 256))  # 2x2x256

            g = tkl.Conv2DTranspose(g, 256, 5, stride=2,  # 7x7x128
                                     activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                     normalizer_params={'scale': True, 'is_training': is_training}, padding='SAME')

            g = tkl.Conv2DTranspose(g, 128, 5, stride=2,  # 14x14x64
                                     activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                     normalizer_params={'scale': True, 'is_training': is_training}, padding='SAME')

            g = tkl.Conv2DTranspose(g, 32, 5, stride=2,  # 14x14x64
                                     activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                     normalizer_params={'scale': True, 'is_training': is_training}, padding='SAME')

            g = tkl.Conv2DTranspose(g, 3, 5, stride=2,  # 28x28x3
                                     activation=tf.nn.tanh, padding='SAME')
            return g

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

class IdentitySVHN(object):
    def __init__(self, y_dim = 10, z_dim = 128, size = 32):
        self.name = 'IdentitySVHN'
        self.z_dim = z_dim
        self.y_dim = y_dim
        self.size = size

    def __call__(self, inputs, is_training = True, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            with tf.variable_scope('base_layers'):
                out = tkl.Conv2D(inputs, num_outputs=64, kernel_size=5, stride=2, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})
                out = tkl.Conv2D(out, num_outputs=128, kernel_size=5, stride=2, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})

                out = tkl.Conv2D(out, num_outputs=256, kernel_size=5, stride=2, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})

                out = tkl.Flatten(out)

                out = tkl.Dense(out, 1024, activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                          normalizer_params={'scale': True, 'is_training': is_training})

                out = tkl.Dense(out, self.z_dim, activation=None)


            with tf.variable_scope('mean_var'):
                mean_c = tf.get_variable('centers_c', [self.y_dim, self.z_dim], dtype=tf.float32,
                                          initializer=tf.contrib.layers.xavier_initializer())
                variance_c_var = tf.get_variable('variance_c', [self.y_dim, self.z_dim], dtype=tf.float32,
                                               initializer=tf.constant_initializer(0.54))
                variance_c = tf.nn.softplus(variance_c_var)
            return out, mean_c, variance_c_var, variance_c

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

    @property
    def mean_var_vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name + '/mean_var')

    @property
    def base_layers_vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name + '/base_layers')

class AttributeSVHN(object):
    def __init__(self, z_dim = 128, size =32):
        self.name = 'AttributeSVHN'
        self.z_dim = z_dim
        self.size = size

    def __call__(self, inputs, is_training = True, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            out = tkl.Conv2D(inputs, num_outputs=64, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})
            out = tkl.Conv2D(out, num_outputs=128, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})

            out = tkl.Conv2D(out, num_outputs=256, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})

            out = tkl.Flatten(out)

            out = tkl.Dense(out, 1024, activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                      normalizer_params={'scale': True, 'is_training': is_training})

            z_mu = tkl.Dense(out, self.z_dim, activation=None)

            z_logvar = tkl.Dense(out, self.z_dim, activation=None)

            return z_mu, z_logvar

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

class EncoderSVHN(object):
    def __init__(self, z_dim = 128, size =32):
        self.name = 'AttributeMnist'
        self.z_dim = z_dim
        self.size = size

    def __call__(self, inputs, y, is_training = True, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            y_shapes = y.get_shape().as_list()
            x_shapes = inputs.get_shape().as_list()
            y = tf.reshape(y, [-1, 1, 1, y_shapes[1]])

            x = tf.concat([inputs, tf.tile(y,[1, x_shapes[1], x_shapes[2], 1])], axis = 3)

            out = tkl.Conv2D(x, num_outputs=64, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})
            out = tkl.Conv2D(out, num_outputs=128, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})

            out = tkl.Conv2D(out, num_outputs=256, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})

            out = tkl.Flatten(out)

            out = tkl.Dense(out, 1024, activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                      normalizer_params={'scale': True, 'is_training': is_training})

            z_mu = tkl.Dense(out, self.z_dim, activation=None)

            z_logvar = tkl.Dense(out, self.z_dim, activation=None)

            return z_mu, z_logvar

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

class DiscriminatorSVHNSN(object):
    def __init__(self, size = 64):
        self.name = 'DiscriminatorSVHNSN'
        self.size = size

    def __call__(self, inputs, y, is_training = True, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()

            out = lrelu(conv(inputs, channels=32, kernel=3, stride=2, pad=1, sn=True, scope='conv_1'))

            out = lrelu(conv(out, channels=128, kernel=3, stride=2, pad=1, sn=True, scope='conv_2'))

            out = lrelu(conv(out, channels=256, kernel=3, stride=1, pad=1, sn=True, scope='conv_3'))

            out = lrelu(conv(out, channels=256, kernel=3, stride=2, pad=1, sn=True, scope='conv_4'))

            out = tkl.AveragePooling2D(out, kernel_size=self.size / (2**3), stride=self.size / (2**3))
            out = tkl.Flatten(out)

            out = lrelu(Dense(out, 1024, sn=True, scope='fc_8'))

            y_proj = Dense(y, 1024, use_bias=False, sn=True, scope='y_proj')
            y_proj = tf.reduce_sum(y_proj * out, axis=1, keep_dims=True)

            d = Dense(out, 1, sn=True, scope='fc_9')
            return d + y_proj

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

class GeneratorSVHNConditionalBN(object):
    def __init__(self, size, category):
        self.name = 'GeneratorSVHNConditionalBN'
        self.size = size
        self.category = category

    def __call__(self, labels, z, is_training = True, reuse = False):
        # labels: shape is [batch_size, 1]. value is in category.
        # 2 fully-connected layers, followed by 6 deconv layers with 2-by-2 upsampling
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()

            w = self.size / (2 ** 4)
           
            out = Dense(z, w*w*256, use_bias=False, sn=False, scope='fc8')
            out = tf.reshape(out, (-1, w, w, 256))
            bn6 = ConditionalBatchNormalization(self.category)
            out = tf.nn.relu(bn6(out, labels=labels, training = is_training))
         
            with tf.name_scope('conv4') as scope:
                out = tkl.Conv2DTranspose(out, num_outputs=256, kernel_size=5, stride=2, activation=None, biases_initializer = None)
                bn4 = ConditionalBatchNormalization(self.category)
                out = tf.nn.relu(bn4(out, labels=labels, training = is_training))

            with tf.name_scope('conv3') as scope:
                out = tkl.Conv2DTranspose(out, num_outputs=128, kernel_size=5, stride=2, activation=None, biases_initializer = None)
                bn3 = ConditionalBatchNormalization(self.category)
                out = tf.nn.relu(bn3(out, labels=labels, training=is_training))

            with tf.name_scope('conv2') as scope:
                out = tkl.Conv2DTranspose(out, num_outputs=32, kernel_size=5, stride=2, activation=None, biases_initializer = None)
                bn2 = ConditionalBatchNormalization(self.category)
                out = tf.nn.relu(bn2(out, labels=labels, training=is_training))

            with tf.name_scope('conv1') as scope:
                 out = tkl.Conv2DTranspose(out,num_outputs=3, kernel_size=5, stride=2, activation=tf.nn.tanh, padding='SAME')

            return out

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)


########################################################
class GeneratorCifar(object):
    def __init__(self, size=28):
        self.name = 'GeneratorCifar'
        self.size = size

    def __call__(self, z_c, z_p, is_training=True, reuse=False):
        # 2 fully-connected layers, followed by 6 deconv layers with 2-by-2 upsampling
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            z = tf.concat([z_c, z_p], axis=1)

            g = tkl.Dense(z, 2 * 2 * 256, activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                    normalizer_params={'scale': True, 'is_training': is_training})
            g = tf.reshape(g, (-1, 2, 2, 256))  # 2x2x256

            g = tkl.Conv2DTranspose(g, 256, 5, stride=2,  # 7x7x128
                                     activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                     normalizer_params={'scale': True, 'is_training': is_training}, padding='SAME')

            g = tkl.Conv2DTranspose(g, 256, 5, stride=1,  # 7x7x128
                                     activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                     normalizer_params={'scale': True, 'is_training': is_training}, padding='SAME')

            g = tkl.Conv2DTranspose(g, 128, 5, stride=2,  # 14x14x64
                                     activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                     normalizer_params={'scale': True, 'is_training': is_training}, padding='SAME')

            g = tkl.Conv2DTranspose(g, 64, 5, stride=2,  # 14x14x64
                                     activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                     normalizer_params={'scale': True, 'is_training': is_training}, padding='SAME')

            g = tkl.Conv2DTranspose(g, 32, 5, stride=2,  # 14x14x64
                                     activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                     normalizer_params={'scale': True, 'is_training': is_training}, padding='SAME')

            g = tkl.Conv2DTranspose(g, 3, 5, stride=1,  # 28x28x3
                                     activation=tf.nn.tanh, padding='SAME')
            return g

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)


class IdentityCifar(object):
    def __init__(self, y_dim=10, z_dim=100, size=28, isrefine=False):
        self.name = 'IdentityCifar'
        self.z_dim = z_dim
        self.y_dim = y_dim
        self.size = size
        self.isrefine = isrefine

    def __call__(self, inputs, is_training=True, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            with tf.variable_scope('base_layers'):
                out = tkl.Conv2D(inputs, num_outputs=32, kernel_size=5, stride=2, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})

                out = tkl.Conv2D(out, num_outputs=64, kernel_size=5, stride=2, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})
                out = tkl.Conv2D(out, num_outputs=128, kernel_size=5, stride=2, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})

                out = tkl.Conv2D(out, num_outputs=256, kernel_size=5, stride=2, activation=tf.nn.relu,
                                 normalizer=tkl.BatchNormalization,
                                 normalizer_params={'scale': True, 'is_training': is_training})

                out = tkl.Flatten(out)

                out = tkl.Dense(out, 1024, activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                          normalizer_params={'scale': True, 'is_training': is_training})

                out = tkl.Dense(out, self.z_dim, activation=None)

            with tf.variable_scope('mean_var'):
                mean_c = tf.get_variable('centers_c', [self.y_dim, self.z_dim], dtype=tf.float32,
                                         initializer=tf.contrib.layers.xavier_initializer())
                variance_c_var = tf.get_variable('variance_c', [self.y_dim, self.z_dim], dtype=tf.float32,
                                                 initializer=tf.constant_initializer(0.54))
                variance_c = tf.nn.softplus(variance_c_var)
            if self.isrefine:
                with tf.variable_scope('mu_logvar'):
                    mu = tkl.Dense(out, self.z_dim, activation=None)
                    logvar = tkl.Dense(out, self.z_dim, activation=None)
                return out, mean_c, variance_c, mu, logvar
            else:
                return out, mean_c, variance_c_var, variance_c

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

    @property
    def mean_var_vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name + '/mean_var')

    @property
    def mu_logvar_vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name + '/mu_logvar')

    @property
    def base_layers_vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name + '/base_layers')


class AttributeCifar(object):
    def __init__(self, z_dim=100, size=28):
        self.name = 'AttributeCifar'
        self.z_dim = z_dim
        self.size = size

    def __call__(self, inputs, is_training=True, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            out = tkl.Conv2D(inputs, num_outputs=32, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})
            out = tkl.Conv2D(out, num_outputs=64, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})
            out = tkl.Conv2D(out, num_outputs=128, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})

            out = tkl.Conv2D(out, num_outputs=256, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})

            out = tkl.Flatten(out)

            out = tkl.Dense(out, 1024, activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                      normalizer_params={'scale': True, 'is_training': is_training})

            z_mu = tkl.Dense(out, self.z_dim, activation=None)

            z_logvar = tkl.Dense(out, self.z_dim, activation=None)

            return z_mu, z_logvar

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

class EncoderCifar(object):
    def __init__(self, z_dim=100, size=28):
        self.name = 'EncoderCifar'
        self.z_dim = z_dim
        self.size = size

    def __call__(self, inputs, y, is_training=True, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            y_shapes = y.get_shape().as_list()
            x_shapes = inputs.get_shape().as_list()
            y = tf.reshape(y, [-1, 1, 1, y_shapes[1]])

            x = tf.concat([inputs, tf.tile(y, [1, x_shapes[1], x_shapes[2], 1])], axis=3)
            out = tkl.Conv2D(x, num_outputs=32, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})
            out = tkl.Conv2D(out, num_outputs=64, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})
            out = tkl.Conv2D(out, num_outputs=128, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})

            out = tkl.Conv2D(out, num_outputs=256, kernel_size=5, stride=2, activation=tf.nn.relu,
                             normalizer=tkl.BatchNormalization,
                             normalizer_params={'scale': True, 'is_training': is_training})

            out = tkl.Flatten(out)

            out = tkl.Dense(out, 1024, activation=tf.nn.relu, normalizer=tkl.BatchNormalization,
                                      normalizer_params={'scale': True, 'is_training': is_training})

            z_mu = tkl.Dense(out, self.z_dim, activation=None)

            z_logvar = tkl.Dense(out, self.z_dim, activation=None)

            return z_mu, z_logvar

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

####################toy

class GeneratorToy(object):
    def __init__(self):
        self.name = 'GeneratorToy'

    def __call__(self, z_c, z_p,reuse = False):
        # 4 fully-connected layers
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            z = tf.concat([z_c, z_p], axis = 1)

            g = tkl.Dense(z, 64, activation=lrelu)

            g = tkl.Dense(g, 64, activation=lrelu)

            g = tkl.Dense(g, 32, activation=lrelu)

            g = tkl.Dense(g, 2, activation=None)

            return g

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

class DiscriminatorToy(object):
    def __init__(self):
        self.name = 'DiscriminatorToy'

    def __call__(self, x, y, reuse=False):
        # DCGAN
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()

            shared = lrelu(Dense(x, 32, sn = True, scope='fc1'))

            shared = lrelu(Dense(shared, 64, sn=True, scope='fc2'))

            shared = lrelu(Dense(shared, 64, sn=True, scope='fc3'))

            y_proj = Dense(y, 64, use_bias=False, sn=True, scope='y_proj')
            y_proj = tf.reduce_sum(y_proj * shared, axis=1, keep_dims=True)

            d = Dense(shared, 1, sn=True, scope='fc4')

            return d + y_proj

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

class IdentityToy(object):
    def __init__(self, y_dim, z_dim):
        self.name = 'IdentityToy'
        self.z_dim = z_dim
        self.y_dim = y_dim

    def __call__(self, x, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            with tf.variable_scope('base_layers'):
                out = tkl.Dense(x, 32, activation=lrelu)

                out = tkl.Dense(out, 64, activation=lrelu)

                out = tkl.Dense(out, 64, activation=lrelu)

                out = tkl.Dense(out, self.z_dim, activation=None)

            with tf.variable_scope('mean_var'):
                mean_c = tf.get_variable('centers_c', [self.y_dim, self.z_dim], dtype=tf.float32,
                                         initializer=tf.contrib.layers.xavier_initializer())
                variance_c_var = tf.get_variable('variance_c', [self.y_dim, self.z_dim], dtype=tf.float32,
                                                 initializer=tf.constant_initializer(0.54))
                variance_c = tf.nn.softplus(variance_c_var)

            return out, mean_c, variance_c_var, variance_c

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

    @property
    def mean_var_vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name + '/mean_var')

    @property
    def base_layers_vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name + '/base_layers')

class AttributeToy(object):
    def __init__(self, z_dim):
        self.name = 'AttributeToy'
        self.z_dim = z_dim

    def __call__(self, x, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            out = tkl.Dense(x, 32, activation=lrelu)

            out = tkl.Dense(out, 64, activation=lrelu)

            out = tkl.Dense(out, 64, activation=lrelu)

            z_mu = tkl.Dense(out, self.z_dim, activation=None)

            z_logvar = tkl.Dense(out, self.z_dim, activation=None)

            return z_mu, z_logvar

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

class EncoderToy(object):
    def __init__(self, z_dim):
        self.name = 'EncoderToy'
        self.z_dim = z_dim

    def __call__(self, x, y, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()

            x = tf.concat([x, y], axis=-1)

            out = tkl.Dense(x, 32, activation=lrelu)

            out = tkl.Dense(out, 64, activation=lrelu)

            out = tkl.Dense(out, 64, activation=lrelu)

            z_mu = tkl.Dense(out, self.z_dim, activation=None)

            z_logvar = tkl.Dense(out, self.z_dim, activation=None)

            return z_mu, z_logvar

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)


class LatentDiscriminatorToy(object):
    def __init__(self, y_dim ):
        self.name = 'LatentDiscriminatorToy'
        self.y_dim = y_dim

    def __call__(self, inputs, reuse=False):
        with tf.variable_scope(self.name) as scope:
            if reuse:
                scope.reuse_variables()
            out = tkl.Dense(inputs, 64, activation=lrelu)
            out = tkl.Dense(out, self.y_dim, activation=None)
            return out
    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)
