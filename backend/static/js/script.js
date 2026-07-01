function addToCart(name, price) {

    let cart = JSON.parse(localStorage.getItem("cart")) || [];

    let product = {
        name: name,
        price: price,
        quantity: 1
    };

    cart.push(product);

    localStorage.setItem("cart", JSON.stringify(cart));

    alert(name + " Added To Cart Successfully");
}

function displayCart() {

    let cart = JSON.parse(localStorage.getItem("cart")) || [];

    let cartItems = document.getElementById("cart-items");

    if (!cartItems) {
        return;
    }

    let total = 0;

    cartItems.innerHTML = "";

    cart.forEach(function(product) {

       total = total + (product.price * product.quantity);
    cartItems.innerHTML += `
    <div class="cart-card">

        <h3>${product.name}</h3>

        <p>Price : ₹${product.price}</p>

        <button onclick="decreaseQuantity('${product.name}')">-</button>

        <span>${product.quantity}</span>

        <button onclick="increaseQuantity('${product.name}')">+</button>

        <p>Total : ₹${product.price * product.quantity}</p>

        <button onclick="removeItem('${product.name}')">
            Remove
        </button>

    </div>
`;
    });

    document.getElementById("total").innerHTML =
`
    <h2 style="text-align:center;color:green;">
    Grand Total : ₹${total}
    </h2>
`;
}

displayCart();
function removeItem(productName) {

    let cart = JSON.parse(localStorage.getItem("cart")) || [];

    cart = cart.filter(function(product) {
        return product.name !== productName;
    });

    localStorage.setItem("cart", JSON.stringify(cart));

    displayCart();
}
function increaseQuantity(productName){

    let cart = JSON.parse(localStorage.getItem("cart")) || [];

    cart.forEach(function(product){

        if(product.name === productName){
            product.quantity = product.quantity + 1;
        }

    });

    localStorage.setItem("cart", JSON.stringify(cart));

    displayCart();
}

function decreaseQuantity(productName){

    let cart = JSON.parse(localStorage.getItem("cart")) || [];

    cart.forEach(function(product){

        if(product.name === productName && product.quantity > 1){
            product.quantity = product.quantity - 1;
        }

    });

    localStorage.setItem("cart", JSON.stringify(cart));

    displayCart();
}