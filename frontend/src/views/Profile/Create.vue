<!-- Create an account profile view -->
<script lang="js" setup>

import { ref, computed } from 'vue'
import { FwbInput, FwbCheckbox, FwbA, FwbButton, FwbRadio } from 'flowbite-vue'
import { AsYouType } from 'libphonenumber-js'
import UserService from '../../services/userService'

const firstName = ref('')
const lastName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const phoneNum = ref('')
const streetAddress = ref('')
const city = ref('')
const state = ref('')
const zipCode = ref('')
const dateOfBirth = ref('')
const siteUsage = ref('')
const termsAndConditions = ref(false)

const passwordMismatch = computed(() => {
    return confirmPassword.value && (password.value !== confirmPassword.value)
})

function formatPhoneNumber(event) {
    const phoneNumberFormatter = new AsYouType("US")
    phoneNum.value = phoneNumberFormatter.input(event.target.value)
}

async function submitAccountForm() {
    // Checking if the password and confirm password match
    if (passwordMismatch.value) {
        alert("Please make sure both password and confirm password match.")
        return
    }

    // Adding a new user to the database
    try {
        await UserService.createUser(
            firstName.value + " " + lastName.value,
            email.value,
            password.value,
            phoneNum.value,
            dateOfBirth.value,
            streetAddress.value,
            city.value,
            state.value,
            zipCode.value,
            siteUsage.value == "Vendor",
            siteUsage.value == "Renter"
        )

        // Resetting the variables back to their default values
        firstName.value = ''
        lastName.value = ''
        email.value = ''
        password.value = ''
        confirmPassword.value = ''
        phoneNum.value = ''
        streetAddress.value = ''
        city.value = ''
        state.value = ''
        zipCode.value = ''
        dateOfBirth.value = ''
        siteUsage.value = ''
        termsAndConditions.value = false

        // Successful account submission
        alert("Account has been successfully created. Please login.")
    }
    catch (error) {
        console.error("Error creating user:", error)

        // Unsuccessful account submission
        alert("Error: Account was not properly created. Please try again.")
    }
}

</script>

<template>
    <h1 class="text-3xl font-bold text-gray-800 mb-6">Create Profile</h1>
    <form class="space-y-4" @submit.prevent="submitAccountForm">
        <div class="grid grid-cols-2 gap-4">
            <fwb-input
                v-model="firstName"
                placeholder="Enter your first name"
                label="First Name"
                required
            />
            <fwb-input
                v-model="lastName"
                placeholder="Enter your last name"
                label="Last Name"
                required
            />
        </div>
        <fwb-input
            v-model="email"
            placeholder="Enter your email address: user@example.com"
            label="Email"
            type="email"
            required
        />
        <fwb-input
            v-model="password"
            placeholder="Enter your password"
            label="Password"
            type="password"
            required
        />
        <fwb-input
            v-model="confirmPassword"
            placeholder="Re-enter your password"
            label="Confirm Password"
            type="password"
            required
        />
        <p v-if="passwordMismatch == true" class="text-red-500 text-sm">
            Passwords do not match
        </p>
        <fwb-input
            v-model="phoneNum"
            placeholder="Enter your phone number"
            label="Phone Number"
            type="tel"
            @input="formatPhoneNumber"
            maxlength="14"
            required
        />
        <div class="grid grid-cols-2 gap-4">
            <fwb-input
                v-model="streetAddress"
                placeholder="Enter your street address"
                label="Street Address"
                required
            />
            <fwb-input
                v-model="city"
                placeholder="Enter your city"
                label="City"
                required
            />
        </div>
        <div class="grid grid-cols-2 gap-4">
            <fwb-input
                v-model="state"
                placeholder="Enter your state"
                label="State"
                required
            />
            <fwb-input
                v-model="zipCode"
                placeholder="Enter your zip code"
                label="Zip Code"
                required
            />
        </div>
        <fwb-input
            v-model="dateOfBirth"
            placeholder="Enter your date of birth"
            label = "Date of Birth"
            type="date"
            required
        />
        <div class="space-y-2">
            <label class="block text-sm font-medium">Site Usage</label>
            <div class="flex w-48">
                <fwb-radio
                    v-model="siteUsage"
                    name="vendor"
                    label="Vendor"
                    value="Vendor"
                />
                <fwb-radio
                    v-model="siteUsage"
                    name="renter"
                    label="Renter"
                    value="Renter"
                />
            </div>
        </div>
        <fwb-checkbox v-model="termsAndConditions" required>
            I agree with
            <fwb-a class="text-blue-600 hover:underline" href="#">
                terms and conditions.
            </fwb-a>
        </fwb-checkbox>
        <fwb-button class="w-24" color="default" pill type="submit">Submit</fwb-button>
    </form>
</template>

<style scoped>

</style>