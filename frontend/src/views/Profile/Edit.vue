<!-- Edit an account details view -->
 <script lang="js" setup>

import { ref, computed, onMounted } from 'vue'
import { FwbInput, FwbButton, FwbRadio, FwbSpinner } from 'flowbite-vue'
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
const userDataLoaded = ref(false)
const userId = 20

const passwordMismatch = computed(() => {
    return confirmPassword.value && (password.value !== confirmPassword.value)
})

function formatPhoneNumber(event) {
    const phoneNumberFormatter = new AsYouType("US")
    phoneNum.value = phoneNumberFormatter.input(event.target.value)
}

async function loadUserDate() {
    try {
        // Getting the user's data
        const userData = await UserService.getUser(userId)

        // Storing the user's data into the component variables
        firstName.value = userData.name.split(' ')[0]
        lastName.value = userData.name.split(' ')[1]
        email.value = userData.email
        password.value = userData.password
        confirmPassword.value = userData.password
        phoneNum.value = userData.phone
        streetAddress.value = userData.street_address
        city.value = userData.city
        state.value = userData.state
        zipCode.value = String(userData.zip_code)
        dateOfBirth.value = userData.date_of_birth
        
        if (userData.vendor == true) {
            siteUsage.value = "Vendor"
        }
        else {
            siteUsage.value = "Renter"
        }

        // Displaying the page to the user
        userDataLoaded.value = true
    }
    catch (error) {
        console.error("Error getting user data:", error)

        // Alerting the user that their data could not be loaded
        alert("Error: Account data could not be loaded.")
    }
}

async function updateAccount() {
    // Checking if the password and confirm password match
    if (passwordMismatch.value) {
        alert("Please make sure both password and confirm password match.")
        return
    }

    // Updating the user's data in the database
    try {
        await UserService.updateUser(
            userId,
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

        // Successful account update
        alert("Account has been successfully updated.")
    }
    catch (error) {
        console.error("Error updating user:", error)

        // Unsuccessful account update
        alert("Error: Account was not properly updated. Please try again.")
    }
}

function cancelUpdate() {

}

onMounted(() => {
    loadUserDate()
})

</script>

<template>
    <h1 class="text-3xl font-bold text-gray-800 mb-6">Edit Profile</h1>
    <div v-if="userDataLoaded == false">
        <fwb-spinner size="12" />
    </div>
    <div v-else>
        <form class="space-y-4">
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
            <div class="flex gap-3">
                <fwb-button class="w-24" color="default" pill @click="cancelUpdate">Cancel</fwb-button>
                <fwb-button class="w-24" color="default" pill type="submit" @click="updateAccount">Save</fwb-button>
            </div>
        </form>
    </div>
</template>

<style scoped>

</style>