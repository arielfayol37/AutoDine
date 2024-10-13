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
            costH.innerHTML = `Total $${data.total.toFixed(2)} (20% after tax)`;
         }
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

    /** 
     * 
     * 
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
      }
      
      // Usage example
      async function demo() {
        console.log('Start');
        moveCardToState("Classic Hot Dog");
        moveCardToState("Burger")
        await sleep(20000); // Sleep for 5 seconds
        removeCardFromState("Classic Hot Dog");
        await sleep(5000);
        removeCardFromState("Burger");
        console.log('End after 10 seconds');
      }
      
      demo();*/    
    
})