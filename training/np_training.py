import numpy as np




values = []

for i in range(12):
    values.append(i)

a = np.array(values)


values = []
for i  in range(10,22):
    values.append(i)

b = np.array(values)

print(f"a ({a.shape}): ", a)
print(f"b ({b.shape}): ", b)


a_matrix = a.reshape(3,4)
b_matrix = b.reshape(3,4)

print(f"a_matrix ({a_matrix.shape}): \n", a_matrix)
print(f"b_matrix ({b_matrix.shape}): \n", b_matrix)





element_wise_sum_matrix = a_matrix + b_matrix
print(f"element_wise_sum_matrix: ", element_wise_sum_matrix)

element_wise_product_matrix = a_matrix * b_matrix
print(f"element_wise_product_matrix: ", element_wise_product_matrix)

print("mean of productmatrix: ", np.mean(element_wise_product_matrix))


print("_____")
print(element_wise_product_matrix[element_wise_product_matrix>100])

