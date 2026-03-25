<!-- View a specific users profile details -->
<script lang="js" setup>

import { ref, onMounted, computed } from 'vue'
import { FwbAvatar, FwbRating, FwbListGroup, FwbListGroupItem, FwbButton } from 'flowbite-vue'
import { useAuthStore } from '../../stores/auth'
import UserService from '../../services/userService'
import router from '../../router'

const auth = useAuthStore()
const userData = ref()
const userDataLoaded = ref(false)

const userId = computed(() => auth.user?.id)
const userPageId = computed(() => auth.user?.id)

function dateFormatting(isoDate) {
    const date = new Date(isoDate)
    return date.toLocaleDateString()
}

function computeAge(dateOfBirth) {
    // Using date objects
    const currentDate = new Date()
    const birthDate = new Date(dateOfBirth)

    // Computing years of age
    let age = currentDate.getFullYear() - birthDate.getFullYear()

    // Subtracting a year if the user's birthday has not occurred
    const hadBirthday = (currentDate.getMonth() > birthDate.getMonth()) || ((currentDate.getMonth() == birthDate.getMonth()) && (currentDate.getDate() >= birthDate.getDate()))

    if (!hadBirthday) {
        age--
    }

    return age
}

function editAccount() {
    router.push({ name: 'edit_profile' })
}

async function loadUserData() {
    try {
        // Getting the user's data
        userData.value = await UserService.getUser(userPageId.value)

        // Displaying the page to the user
        userDataLoaded.value = true
    }
    catch (error) {
        console.error("Error getting user data:", error)

        // Alerting the user that the user's data could not be loaded
        alert("Error: Account data could not be loaded.")
    }
}

onMounted(async () => {
    await loadUserData()
})

</script>

<template>
    <div v-if="userDataLoaded == false">
        <fwb-spinner size="12" />
    </div>
    <div v-else>
        <div class="space-y-4">

            <!-- ************************************************* -->
            <!-- Avatar code needs to be updated in a later sprint -->
            <!-- ************************************************* -->
            <fwb-avatar bordered size="xl" img="" />

            <h1 class="text-3xl font-bold text-gray-800 mb-6">{{ userData.name }}</h1>

            <!-- ********************************************************* -->
            <!-- Ratings code needs to be updated when it gets implemented -->
            <!-- ********************************************************* -->
            <fwb-rating :rating="0.0" review-link="#" review-text="0 reviews">
                <template #besideText>
                    <p class="ml-2 text-sm font-medium text-gray-500 dark:text-gray-400">
                        0.0 out of 5
                    </p>
                </template>
            </fwb-rating>

            <div v-if="userId != userPageId">
                <fwb-list-group class="w-auto">
                    <fwb-list-group-item><b>Email</b>: {{ userData.email }}</fwb-list-group-item>
                    <fwb-list-group-item><b>Phone Number</b>: {{ userData.phone }}</fwb-list-group-item>
                    <fwb-list-group-item><b>State</b>: {{ userData.state }}</fwb-list-group-item>
                    <fwb-list-group-item><b>Age</b>: {{ computeAge(userData.date_of_birth) }} years</fwb-list-group-item>
                    <fwb-list-group-item><b>User Type</b>: {{ (userData.vendor == true) ? 'Vendor' : 'Renter' }}</fwb-list-group-item>
                    <fwb-list-group-item><b>Date Joined</b>: {{ dateFormatting(userData.created_at) }}</fwb-list-group-item>
                </fwb-list-group>
            </div>
            <div v-else class="space-y-4">
                <fwb-list-group class="w-auto">
                    <fwb-list-group-item><b>Email</b>:  {{ userData.email }}</fwb-list-group-item>
                    <fwb-list-group-item><b>Phone Number</b>: {{ userData.phone }}</fwb-list-group-item>
                    <fwb-list-group-item><b>Street Address</b>: {{ userData.street_address }}</fwb-list-group-item>
                    <fwb-list-group-item><b>City</b>: {{ userData.city }}</fwb-list-group-item>
                    <fwb-list-group-item><b>State</b>: {{ userData.state }}</fwb-list-group-item>
                    <fwb-list-group-item><b>Zip Code</b>: {{ userData.zip_code }}</fwb-list-group-item>
                    <fwb-list-group-item><b>Age</b>: {{ computeAge(userData.date_of_birth) }} years</fwb-list-group-item>
                    <fwb-list-group-item><b>User Type</b>: {{ (userData.vendor == true) ? 'Vendor' : 'Renter' }}</fwb-list-group-item>
                    <fwb-list-group-item><b>Date Joined</b>: {{ dateFormatting(userData.created_at) }}</fwb-list-group-item>
                </fwb-list-group>
                <fwb-button class="w-24" color="default" pill @click="editAccount">Edit</fwb-button>
            </div>
        </div>
    </div>
</template>

<style scoped>

</style>