<!-- Complete profile after registration/OAuth -->
<script lang="js" setup>

import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { FwbInput, FwbCheckbox, FwbA, FwbButton, FwbRadio } from 'flowbite-vue'
import { AsYouType } from 'libphonenumber-js'
import { useAuthStore } from '../../stores/auth'
import UserService from '../../services/userService'
import authService from '../../services/authService'

const router = useRouter()
const auth = useAuthStore()

const firstName = ref('')
const lastName = ref('')
const phoneNum = ref('')
const streetAddress = ref('')
const city = ref('')
const state = ref('')
const zipCode = ref('')
const dateOfBirth = ref('')
const siteUsage = ref('')
const termsAndConditions = ref(false)

onMounted(() => {
    if (!auth.isAuthenticated) {
        router.push({ name: 'login' })
        return
    }

    // Pre-fill name from the authenticated user
    if (auth.user?.name) {
        const parts = auth.user.name.split(' ')
        firstName.value = parts[0] || ''
        lastName.value = parts.slice(1).join(' ') || ''
    }
})

function formatPhoneNumber(event) {
    const digits = event.target.value.replace(/\D/g, '').slice(0, 10)
    if (!digits) {
        phoneNum.value = ''
        return
    }
    if (digits.length <= 3) phoneNum.value = `(${digits}`
    else if (digits.length <= 6) phoneNum.value = `(${digits.slice(0, 3)}) ${digits.slice(3)}`
    else phoneNum.value = `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`
}

async function submitProfile() {
    try {
        await UserService.updateUser(
            auth.user.id,
            firstName.value + " " + lastName.value,
            auth.user.email,
            null,
            phoneNum.value,
            dateOfBirth.value,
            streetAddress.value,
            city.value,
            state.value,
            zipCode.value,
            siteUsage.value === "Vendor",
            siteUsage.value === "Renter"
        )

        // Refresh user data in the auth store
        const user = await authService.getMe()
        auth.setAuth({
            access_token: auth.accessToken,
            refresh_token: auth.refreshToken,
            user
        })

        router.push('/')
    }
    catch (error) {
        console.error("Error completing profile:", error)
        alert("Error: Profile could not be saved. Please try again.")
    }
}

</script>

<template>
    <div class="max-w-2xl mx-auto">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">Complete Your Profile</h1>
        <p class="text-gray-600 mb-6">Please fill in the remaining details to get started.</p>
        <form class="space-y-4" @submit.prevent="submitProfile">
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
                label="Date of Birth"
                type="date"
                required
            />
            <div class="space-y-2">
                <label class="block text-sm font-medium">I want to use the site as a:</label>
                <div class="flex w-48">
                    <fwb-radio
                        v-model="siteUsage"
                        name="siteUsage"
                        label="Vendor"
                        value="Vendor"
                    />
                    <fwb-radio
                        v-model="siteUsage"
                        name="siteUsage"
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
            <fwb-button class="w-full" color="default" type="submit">Complete Profile</fwb-button>
        </form>
    </div>
</template>
