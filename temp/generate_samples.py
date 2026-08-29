from PIL import Image, ImageDraw
import fitz

def create_slide_image(title, bullet_points, filename, bg_color=(245, 247, 250), text_color=(30, 41, 59)):
    img = Image.new(RGB, (1000, 650), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Title card
    draw.rectangle([(40, 30), (960, 110)], fill=(224, 231, 255), outline=(99, 102, 241), width=2)
    draw.text((60, 55), str(title), fill=(30, 27, 75))
    
    y = 150
    for idx, bp in enumerate(bullet_points, 1):
        draw.rectangle([(50, y-5), (950, y+55)], fill=(255, 255, 255), outline=(226, 232, 240), width=1)
        draw.text((70, y+15), str(idx) + .  + str(bp), fill=text_color)
        y += 75
        
    img.save(filename)
    return img

print(Creating sample test slides and PDF...)
img1 = create_slide_image(Introduction to Neural Networks, [
    Neurons receive inputs x_i and compute weighted sums.,
    Activation functions like ReLU and Sigmoid introduce non-linearity.,
    Loss functions evaluate error between predictions and ground truth.
], temp/slide1_nn_intro.png)

img2 = create_slide_image(Introduction to Neural Networks, [
    Neurons receive inputs x_i and compute weighted sums.,
    Activation functions like ReLU and Sigmoid introduce non-linearity.,
    Loss functions evaluate error between predictions and ground truth.
], temp/slide2_nn_intro_dup.png)

img3 = create_slide_image(Backpropagation and Gradient Descent, [
    Backpropagation computes the gradient of the loss function using chain rule.,
    Learning rate controls step size during weight update.,
    Stochastic Gradient Descent (SGD) and Adam are common optimizers.
], temp/slide3_backprop.png)

doc = fitz.open()
page1 = doc.new_page(width=1000, height=650)
page1.insert_text((60, 80), Machine Learning Basics - Chapter 1, fontsize=24)
page1.insert_text((70, 180), 1. Supervised Learning: Labeled training dataset (X, y), fontsize=16)
page1.insert_text((70, 240), 2. Unsupervised Learning: Discovering hidden patterns in X, fontsize=16)
page1.insert_text((70, 300), 3. Reinforcement Learning: Agent interacting with environment, fontsize=16)

page2 = doc.new_page(width=1000, height=650)
page2.insert_text((60, 80), Supervised Learning Algorithms, fontsize=24)
page2.insert_text((70, 180), 1. Linear Regression: Predicts continuous numerical targets, fontsize=16)
page2.insert_text((70, 240), 2. Logistic Regression: Classification via sigmoid probabilities, fontsize=16)
page2.insert_text((70, 300), 3. Decision Trees and Random Forests: Non-linear partitioning, fontsize=16)

doc.save(temp/sample_lecture_deck.pdf)
doc.close()

print(Generated sample slides and PDF successfully!)
