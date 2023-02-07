import numpy as np
from paddle.inference import Config
from paddle.inference import create_predictor

config = Config("inference_model/LSTMModel.pdmodel", "inference_model/LSTMModel.pdiparams")
config.disable_gpu()

# 创建 PaddlePredictor
predictor = create_predictor(config)

# 获取输入的名称
input_names = predictor.get_input_names()
input_handle = predictor.get_input_handle(input_names[0])

# 设置输入
# fake_input = np.random.randn(1, 1, 28, 28).astype("float32")
fake_input = np.array([[[0.02436546,-3.54048419,9.99999996,10.00000008]]]).astype('float32')
# input_handle.reshape([1, 1, 28, 28])
input_handle.copy_from_cpu(fake_input)

# 运行 predictor
predictor.run()

# 获取输出
output_names = predictor.get_output_names()
output_handle = predictor.get_output_handle(output_names[0])
output_data = output_handle.copy_to_cpu() # numpy.ndarray 类型

print(output_data)
# 0.16829303 -0.04975733
# -0.0488644 -3.8709748