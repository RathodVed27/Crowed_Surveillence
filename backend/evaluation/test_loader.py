from shanghai_loader import ShanghaiLoader

loader = ShanghaiLoader(
    r"C:\Users\hp\Desktop\crowed density\Sanghai DataSet\ShanghaiTech"
)

image_path = r"C:\Users\hp\Desktop\crowed density\Sanghai DataSet\ShanghaiTech\part_A\test_data\images\IMG_99.jpg"

count = loader.get_actual_count(image_path)

print("Actual People:", count)