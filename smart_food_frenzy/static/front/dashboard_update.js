document.addEventListener('DOMContentLoaded', function() {

    // Connect to the Django server via the SSE endpoint
    const eventSource = new EventSource('http://localhost:8000/sse/');

    // Handle the event when a new message is received from the server
    eventSource.onmessage = function(event) {
        updateDashboard(JSON.parse(event.data));
        
    };

    // Handle errors in case the connection fails
    eventSource.onerror = function(err) {
        console.error("EventSource failed:", err);
        eventSource.close();
    };    


    function updateDashboard(data) {
        const statusBar = document.querySelector(".thinkingBar")
        if(data.thinking == true){
            statusBar.classList.remove("hide");
            statusBar.classList.add("orange");
            statusBar.classList.remove("blue")
        }else if(data.recording == true){
            statusBar.classList.remove("hide");
            statusBar.classList.add("blue");
            statusBar.classList.remove("orange");
        }else{
            statusBar.classList.add("hide");
        }
        // Handle items to add to the dashboard (currentState div)
        data.add_to_db.forEach(item => {
            const name = item.name;  // Get the item name
            moveCardToState(name);   // Move the card to currentState
        });
    
        // Handle items to remove from the dashboard (currentState div)
        data.remove_from_db.forEach(item => {
            const name = item.name;  // Get the item name
            removeCardFromState(name);  // Move the card back to the container
        });

        const costH = document.querySelector(".totalCost");
        if (data.total == 0){
            costH.innerHTML = `Total #.#`;  
        }
        else{
            
            if (data.total == -17){
                restoreAllStateItems();
                costH.innerHTML = `Total #.#`;
            }else{
                costH.innerHTML = `Total $${data.total.toFixed(2)} (20% tax)`;
            }
            
         }
         document.querySelector(".orderDetails").innerHTML = `${data.order_details}`;
    }
    

    function moveCardToState(name) {
        // Find the card using the name as the image id
        const inputField = document.querySelector(`input[value="${name}"]`);
        const card = inputField.closest('.card');
        // If card exists, proceed
        if (card) {
            // Hide the original card
            card.classList.add('hide')
    
            // Clone the card
            const cardClone = card.cloneNode(true);
            const rating = cardClone.querySelector(".rating");
            if (rating != null){
                rating.remove();
            }
            const priceTag = cardClone.querySelector(".priceTag");
            if (priceTag != null){
                priceTag.remove();
            }
            
            // Add the "stateItem" class to the cloned card
            cardClone.classList.add('stateItem');
            cardClone.classList.remove("card", "hide")
            
            // Append the cloned card to the currentState div
            const currentStateDiv = document.querySelector('.currentState');
            currentStateDiv.appendChild(cardClone);
        } else {
            console.log(`Card with name "${name}" not found`);
        }
    }

    function removeCardFromState(name) {
        // Find the card in the "currentState" div using the input value attribute
        const currentStateDiv = document.querySelector('.currentState');
        const inputFieldInState = currentStateDiv.querySelector(`input[value="${name}"]`);
        const stateItem = inputFieldInState ? inputFieldInState.closest('.stateItem') : null;
    
        // If the card exists in currentState, remove it
        if (stateItem) {
            currentStateDiv.removeChild(stateItem);
        } else {
            console.log(`Card with name "${name}" not found in currentState`);
        }
    
        // Restore the visibility of the original card in the container div
        const containerCard = document.querySelector(`input[value="${name}"]`).closest('.card');
        if (containerCard) {
            containerCard.classList.remove('hide')
        } else {
            console.log(`Card with name "${name}" not found in container`);
        }
    }

    function restoreAllStateItems() {
        // Get all the stateItem elements in the currentState div
        const currentStateDiv = document.querySelector('.currentState');
        const stateItems = currentStateDiv.querySelectorAll('.stateItem');
    
        // Iterate over each stateItem and move it back to the container
        stateItems.forEach(stateItem => {
            // Find the corresponding input field to get the name of the item
            const inputField = stateItem.querySelector('input');
            const name = inputField ? inputField.value : null;
    
            if (name) {
                // Remove the stateItem from currentState
                currentStateDiv.removeChild(stateItem);
    
                // Restore the original card in the container div
                const containerCard = document.querySelector(`input[value="${name}"]`).closest('.card');
                if (containerCard) {
                    containerCard.classList.remove('hide');
                } else {
                    console.log(`Card with name "${name}" not found in container`);
                }
            }
        });
    }
    
})