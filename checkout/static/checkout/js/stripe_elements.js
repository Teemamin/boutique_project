/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment
    CSS from here: 
    https://stripe.com/docs/stripe-js
*/
/**
 * gets the stripe public key and client secret from the template using  jQuery.
 * see notes for further explanation on how to get cleintsecret
 * and removes(slice) the qotation marks at the beginin n end 
 */
var stripePublic_key = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);
// made possible by the stripe js included in the base template.
// sets up stripe is create a variable using our stripe public key.
var stripe = Stripe(stripePublic_key);
//Now we can use it to create an instance of stripe elements.
var elements = stripe.elements();
var style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};
// Using the strip instance above to create a card element.
var card = elements.create('card', {style: style});
//mount the card element to the div we created in checkout.html
card.mount('#card-element');

// Handle realtime validation errors on the card element
card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    if (event.error) {
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = '';
    }
});

// Handle form submit
// most of this comes from the strip docs
var form = document.getElementById('payment-form');

form.addEventListener('submit', function(ev) {
    ev.preventDefault();
    // disable the card element n submit btn b4 callin 
    // out to stripe to avoid multiple submissions
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true);
    $('#payment-form').fadeToggle(100); //to fadeout the payment form wen user submits
    $('#loading-overlay').fadeToggle(100); // activate the overlay div
    // gets the boolean value of save info to see if it is chkd or not
    var saveInfo = Boolean($('#id-save-info').attr('checked'));
    // From using {% csrf_token %} in the form(django genereates that on our form)
    // it gets tha value of our csrf frm the form input feild
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    // postdata objct to pass to our cache view
    var postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
    };
    // cache view url
    var url = '/checkout/cache_checkout_data/';
    // using jquery post: post the postdata to the url but wait for a response that payment intent was updated
    //  if our view returns a stutus of 200 ok beofre calling the confirm payment method
    //.done method used to achieve the wait.
    $.post(url, postData).done(function () {
        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: { //see note for further explanations
                    name: $.trim(form.full_name.value),
                    phone: $.trim(form.phone_number.value),
                    email: $.trim(form.email.value),
                    address:{
                        line1: $.trim(form.street_address1.value),
                        line2: $.trim(form.street_address2.value),
                        city: $.trim(form.town_or_city.value),
                        country: $.trim(form.country.value),
                        state: $.trim(form.county.value),
                    }
                }
            },
            shipping: {
                name: $.trim(form.full_name.value),
                phone: $.trim(form.phone_number.value),
                address: {
                    line1: $.trim(form.street_address1.value),
                    line2: $.trim(form.street_address2.value),
                    city: $.trim(form.town_or_city.value),
                    country: $.trim(form.country.value),
                    postal_code: $.trim(form.postcode.value),
                    state: $.trim(form.county.value),
                }
            },
        }).then(function(result) {
            if (result.error) {
                var errorDiv = document.getElementById('card-errors');
                var html = `
                    <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                    </span>
                    <span>${result.error.message}</span>`;
                $(errorDiv).html(html);
                $('#payment-form').fadeToggle(100); // reverse wen there is an error
                $('#loading-overlay').fadeToggle(100);
                // if there is an error we will reenable the card element
                // and submit btn to allow the user to fix it
                card.update({ 'disabled': false});
                $('#submit-button').attr('disabled', false);
            } else {
                if (result.paymentIntent.status === 'succeeded') {
                    form.submit();
                }
            }
        });
    }).fail(function () {
        // if our view returns 400 bad request response 
        // just reload the page, n show in django messages
        location.reload();
    })
});