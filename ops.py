import tensorflow as tf

weight_init = tf.random_normal_initializer(mean=0.0, stddev=0.02)
weight_regularizer = None

def conv(x, channels, kernel=4, stride=2, pad=0, pad_type='zero', use_bias=True, sn=False, scope='conv_0'):
    with tf.variable_scope(scope):
        if pad_type == 'zero' :
            x = tf.pad(x, [[0, 0], [pad, pad], [pad, pad], [0, 0]])
        if pad_type == 'reflect' :
            x = tf.pad(x, [[0, 0], [pad, pad], [pad, pad], [0, 0]], mode='REFLECT')

        if sn :
            w = tf.get_variable("kernel", shape=[kernel, kernel, x.get_shape()[-1], channels], initializer=weight_init,
                                regularizer=weight_regularizer)
            bias = tf.get_variable("bias", [channels], initializer=tf.constant_initializer(0.0))
            x = tf.nn.conv2d(input=x, filter=spectral_norm(w),
                             strides=[1, stride, stride, 1], padding='VALID')
            if use_bias :
                x = tf.nn.bias_add(x, bias)

        else :
            x = tf.layers.conv2d(inputs=x, filters=channels,
                                 kernel_size=kernel, kernel_initializer=weight_init,
                                 kernel_regularizer=weight_regularizer,
                                 strides=stride, use_bias=use_bias)



        return x

def deconv(x, channels, kernel=4, stride=2, use_bias=True, sn=False, scope='deconv_0'):
    with tf.variable_scope(scope):
        x_shape = x.get_shape().as_list()
        output_shape = [x_shape[0], x_shape[1] * stride, x_shape[2] * stride, channels]
        if sn :
            w = tf.get_variable("kernel", shape=[kernel, kernel, channels, x.get_shape()[-1]], initializer=weight_init, regularizer=weight_regularizer)
            x = tf.nn.conv2d_transpose(x, filter=spectral_normed_weight(w), output_shape=output_shape, strides=[1, stride, stride, 1], padding='SAME')

            if use_bias :
                bias = tf.get_variable("bias", [channels], initializer=tf.constant_initializer(0.0))
                x = tf.nn.bias_add(x, bias)

        else :
            x = tf.layers.conv2d_transpose(inputs=x, filters=channels,
                                           kernel_size=kernel, kernel_initializer=weight_init, kernel_regularizer=weight_regularizer,
                                           strides=stride, padding='SAME', use_bias=use_bias)

        return x

def max_pooling(x, kernel=2, stride=2) :
    return tf.layers.max_pooling2d(x, pool_size=kernel, strides=stride)

def avg_pooling(x, kernel=2, stride=2) :
    return tf.layers.average_pooling2d(x, pool_size=kernel, strides=stride)

def global_avg_pooling(x):
    """
    Incoming Tensor shape must be 4-D
    """
    gap = tf.reduce_mean(x, axis=[1, 2])
    return gap

def fully_connected(x, units, use_bias=True, sn=False, scope='fully_0'):
    with tf.variable_scope(scope):
        x = flatten(x)
        shape = x.get_shape().as_list()
        channels = shape[-1]

        if sn :
            w = tf.get_variable("kernel", [channels, units], tf.float32,
                                     initializer=weight_init, regularizer=weight_regularizer)
            if use_bias :
                bias = tf.get_variable("bias", [units],
                                       initializer=tf.constant_initializer(0.0))

                x = tf.matmul(x, spectral_norm(w)) + bias
            else :
                x = tf.matmul(x, spectral_norm(w))

        else :
            x = tf.layers.dense(x, units=units, kernel_initializer=weight_init, kernel_regularizer=weight_regularizer, use_bias=use_bias)

        return x


def flatten(x) :
    return tf.keras.layers.Flatten(x)

def lrelu(x, leak=0.1, name="lrelu"):
    with tf.variable_scope(name):
        f1 = 0.5 * (1 + leak)
        f2 = 0.5 * (1 - leak)
    return f1 * x + f2 * abs(x)

def relu(x):
    return tf.nn.relu(x)


def sigmoid(x):
    return tf.sigmoid(x)


def tanh(x):
    return tf.tanh(x)


def swish(x):
    return x * sigmoid(x)

def discriminator_loss(real, fake):
    real_loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.ones_like(real), logits=real))
    fake_loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.zeros_like(fake), logits=fake))
    loss = real_loss + fake_loss

    return loss


def generator_loss(fake):
    loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.ones_like(fake), logits=fake))

    return loss



def batch_norm(x, scope='BatchNorm'):
    return tf.keras.layers.BatchNormalization(x,
                                        decay=0.9, epsilon=1e-05,
                                        center=True, scale=True, trainable=True,
                                        scope=scope)


def instance_norm(x, scope='GroupNormalization'):
    return tf.keras.layers.GroupNormalization (x,
                                           epsilon=1e-05,
                                           center=True, scale=True,
                                           scope=scope)

def layer_norm(x, scope='layer_norm') :
    return tf.keras.layers.LayerNormalization(x,
                                        center=True, scale=True,
                                        scope=scope)

def group_norm(x, G=32, eps=1e-5, scope='group_norm') :
    with tf.variable_scope(scope) :
        N, H, W, C = x.get_shape().as_list()
        G = min(G, C)

        x = tf.reshape(x, [N, H, W, G, C // G])
        mean, var = tf.nn.moments(x, [1, 2, 4], keep_dims=True)
        x = (x - mean) / tf.sqrt(var + eps)

        gamma = tf.get_variable('gamma', [1, 1, 1, C],
                                initializer=tf.constant_initializer(1.0))
        beta = tf.get_variable('beta', [1, 1, 1, C],
                               initializer=tf.constant_initializer(0.0))
        # gamma = tf.reshape(gamma, [1, 1, 1, C])
        # beta = tf.reshape(beta, [1, 1, 1, C])

        x = tf.reshape(x, [N, H, W, C]) * gamma + beta

    return x


def l2_norm(v, eps=1e-12):
    return v / (tf.reduce_sum(v ** 2) ** 0.5 + eps)

def spectral_norm(w, iteration=1):
    w_shape = w.shape.as_list()
    w = tf.reshape(w, [-1, w_shape[-1]])

    u = tf.get_variable("u", [1, w_shape[-1]], initializer=tf.truncated_normal_initializer(), trainable=False)

    u_hat = u
    v_hat = None
    for i in range(iteration):
        """
        power iteration
        Usually iteration = 1 will be enough
        """
        v_ = tf.matmul(u_hat, tf.transpose(w))
        v_hat = l2_norm(v_)

        u_ = tf.matmul(v_hat, w)
        u_hat = l2_norm(u_)

    sigma = tf.matmul(tf.matmul(v_hat, w), tf.transpose(u_hat))
    w_norm = w / sigma

    with tf.control_dependencies([u.assign(u_hat)]):
        w_norm = tf.reshape(w_norm, w_shape)

    return w_norm


def L1_loss(x, y):
    loss = tf.reduce_mean(tf.abs(x - y))

    return loss

def L2_loss(x, y):
    loss = tf.reduce_mean(tf.square(x - y))
    # if len(x.get_shape().as_list()) == 4:
    #     loss = 0.5 * tf.reduce_mean(tf.reduce_sum(tf.square(x - y), axis = [1,2,3]))
    # elif len(x.get_shape().as_list()) == 2:
    #     loss = 0.5 * tf.reduce_mean(tf.reduce_sum(tf.square(x - y), axis= [1]))
    return loss
