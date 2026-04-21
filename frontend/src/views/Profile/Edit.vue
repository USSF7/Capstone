<!-- Edit an account details view -->
<script lang="js" setup>

import { ref, onMounted, computed } from 'vue'
import { FwbInput, FwbButton, FwbCheckbox, FwbSpinner, FwbAvatar, FwbFileInput } from 'flowbite-vue'
import { DocumentArrowUpIcon } from '@heroicons/vue/24/solid'
import { useAuthStore } from '../../stores/auth'
import UserService from '../../services/userService'
import AuthService from '../../services/authService'
import router from '../../router'

/**
 * Backend base URL for serving uploaded profile images.
 */
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL

/**
 * Maximum allowed profile picture size (2MB).
 */
const MAX_FILE_SIZE = 2 * 1024 * 1024

/**
 * Auth store providing current logged-in user.
 */
const auth = useAuthStore()

/**
 * First name field.
 */
const firstName = ref('')

/**
 * Last name field.
 */
const lastName = ref('')

/**
 * Email field.
 */
const email = ref('')

/**
 * Phone number field.
 */
const phoneNum = ref('')

/**
 * Street address field.
 */
const streetAddress = ref('')

/**
 * City field.
 */
const city = ref('')

/**
 * State field.
 */
const state = ref('')

/**
 * Zip code field.
 */
const zipCode = ref('')

/**
 * Date of birth field.
 */
const dateOfBirth = ref('')

/**
 * User role vendor status.
 */
const vendorStatus = ref(false)

/**
 * User role renter status.
 */
const renterStatus = ref(false)

/**
 * User data loaded state.
 */
const userDataLoaded = ref(false)

/**
 * Uploaded profile picture filename stored in backend
 */
const picture = ref('')

/**
 * State for displaying the file upload button.
 */
const displayFileUploadButton = ref(true)

/**
 * State for displaying the file upload box.
 */
const displayFileUploadBox = ref(false)

/**
 * State for displaying the file upload spinner.
 */
const displayFileUploadSpinner = ref(false)

/**
 * State for displaying the user's uploaded picture file.
 */
const displayFileUploadPhoto = ref(false)

/**
 * Whether selected file passes validation.
 */
const canUploadPhoto = ref(false)

/**
 * Selected image file before it is uploaded.
 */
const userPhoto = ref(null)

/**
 * Gets the user's ID from auth.
 */
const userId = computed(() => auth.user?.id)

/**
 * Ensures at least one user role is selected.
 */
const isUserTypeValid = computed(() => {
    return vendorStatus.value || renterStatus.value
})

/**
 * Formats phone number input into (XXX) XXX-XXXX format.
 */
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

/**
 * Loads the user's current data.
 */
async function loadUserData() {
    try {
        // Getting the user's data
        const userData = await UserService.getUser(userId.value)

        // Storing the user's data into the component variables
        const parts = (userData.name || '').split(' ')
        firstName.value = parts[0] || ''
        lastName.value = parts.slice(1).join(' ') || ''
        email.value = userData.email
        phoneNum.value = userData.phone
        streetAddress.value = userData.street_address
        city.value = userData.city
        state.value = userData.state
        zipCode.value = String(userData.zip_code)
        dateOfBirth.value = userData.date_of_birth
        vendorStatus.value = userData.vendor
        renterStatus.value = userData.renter
        picture.value = userData.picture

        // If the equipment already has a picture, then display it.
        if (picture.value !== '') {
            displayFileUploadButton.value = false
            displayFileUploadBox.value = false
            displayFileUploadPhoto.value = true
            displayFileUploadSpinner.value = false
            canUploadPhoto.value = false
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

/**
 * Submits updated profile data to the backend.
 */
async function updateAccount(event) {
    event.preventDefault()

    // Updating the user's data in the database
    try {
        await UserService.updateUser(
            userId.value,
            firstName.value + " " + lastName.value,
            email.value,
            phoneNum.value,
            dateOfBirth.value,
            streetAddress.value,
            city.value,
            state.value,
            zipCode.value,
            vendorStatus.value,
            renterStatus.value,
            picture.value
        )

        // Refresh user data in the auth store
        const user = await AuthService.getMe()
        auth.setAuth({
            access_token: auth.accessToken,
            refresh_token: auth.refreshToken,
            user
        })

        // Successful account update
        alert("Account has been successfully updated.")

        // Going back to the view profile page
        router.push({ name: 'view_profile', params: { id: userId.value } })
    }
    catch (error) {
        console.error("Error updating user:", error)

        // Unsuccessful account update
        alert("Error: Account was not properly updated. Please try again.")
    }
}

/**
 * Cancels the account update and directs the user back to the view profile page.
 */
function cancelUpdate() {
    router.push({ name: 'view_profile', params: { id: userId.value } })
}

/**
 * Switches user interface into file upload mode.
 */
function onClickDisplayFileUploadBox() {
  displayFileUploadButton.value = false
  displayFileUploadBox.value = true
  displayFileUploadSpinner.value = false
  displayFileUploadPhoto.value = false
  canUploadPhoto.value = false
}

/**
 * Resets upload state and removes selected file.
 */
function onClickDisplayFileUploadButton() {
  displayFileUploadButton.value = true
  displayFileUploadBox.value = false
  displayFileUploadSpinner.value = false
  displayFileUploadPhoto.value = false
  canUploadPhoto.value = false

  // Setting the equipment picture reference back to null
  userPhoto.value = null

  // Setting the equipment picture dirctory back to an empty string
  picture.value = ''
}

/**
 * Validates selected image file.
 */
function handleFileChange(event) {
  // Getting the file
  const file = event.target.files[0]

  if (!file) {
    return
  }

  // Validating that the file is the correct file type
  const allowedTypes = [
    'image/jpeg',
    'image/png',
    'image/webp'
  ]

  if (allowedTypes.includes(file.type) == false) {
    canUploadPhoto.value = false
    userPhoto.value = null
    alert('Invalid file type. Please upload JPG, PNG, or WebP.')
    return
  }

  // Validating that the file is not too large
  if (file.size > MAX_FILE_SIZE) {
    canUploadPhoto.value = false
    userPhoto.value = null
    alert("The inputted picture file is too large. The maximum file size is 2 MB.")
    return
  }

  // Allowing the user to upload the file
  canUploadPhoto.value = true
}

/**
 * Uploads image to backend and stores returned filename in form.
 */
async function onClickUploadFile() {
  displayFileUploadButton.value = false
  displayFileUploadBox.value = false
  displayFileUploadPhoto.value = false
  displayFileUploadSpinner.value = true
  canUploadPhoto.value = false

  // Sending the picture to be saved in the backend
  const file = userPhoto.value
  let result = await UserService.uploadUserPicture(file)

  // Checking if the picture was successfully stored in the backend
  if (result.success == false) {
    alert("Picture file did not upload properly. Please try again.")

    // Resetting to the file upload box
    onClickDisplayFileUploadBox()

    // Setting the equipment picture reference back to null
    userPhoto.value = null

    // Setting the equipment picture dirctory back to an empty string
    picture.value = ''

    return
  }

  // Storing the picture filepath in the form object for the equipment
  picture.value = result.filename

  // Displaying the picture to the user
  displayFileUploadSpinner.value = false
  displayFileUploadPhoto.value = true
}

/**
 * Deletes uploaded image and resets state.
 */
async function onClickCancelUploadedFile() {
  displayFileUploadButton.value = true
  displayFileUploadBox.value = false
  displayFileUploadPhoto.value = false
  displayFileUploadSpinner.value = false
  canUploadPhoto.value = false

  // Setting the equipment picture reference back to null
  userPhoto.value = null

  // Delete the photo from the backend
  let result = await UserService.deleteUploadedUserPicture(picture.value)
  
  // Setting the equipment picture dirctory back to an empty string
  picture.value = ''
}

/**
 * Re-opens upload flow and removes previously uploaded image.
 */
async function onClickReuploadFile() {
  displayFileUploadButton.value = false
  displayFileUploadBox.value = true
  displayFileUploadPhoto.value = false
  displayFileUploadSpinner.value = false
  canUploadPhoto.value = false

  // Setting the equipment picture reference back to null
  userPhoto.value = null

  // Delete the photo from the backend
  let result = await UserService.deleteUploadedUserPicture(picture.value)

  // Setting the equipment picture dirctory back to an empty string
  picture.value = ''
}

/**
 * Load user data when component mounts.
 */
onMounted(async () => {
    await loadUserData()
})

</script>

<template>
    <h1 class="text-3xl font-bold text-gray-800 mb-6">Edit Profile</h1>
    <div v-if="userDataLoaded == false">
        <fwb-spinner size="12" />
    </div>
    <div v-else>
        <form class="space-y-4" @submit.prevent="updateAccount">
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
                <p class="text-xs text-gray-500">
                    This setting controls which navigation items are shown.
                </p>
                <div class="flex w-48">
                    <fwb-checkbox
                        v-model="vendorStatus"
                        name="vendor"
                        label="Vendor"
                    />
                    <fwb-checkbox
                        v-model="renterStatus"
                        name="renter"
                        label="Renter"
                    />
                </div>
            </div>
            <div class="mb-4" v-if="displayFileUploadButton == true">
                <label class="block mb-2 text-sm font-medium text-black-700">
                    Upload Profile Picture (.jpeg / .jpg / .png / .webp)
                </label>
                <fwb-button
                    @click="onClickDisplayFileUploadBox"
                    color="blue"
                    size="md"
                    square
                >
                    <DocumentArrowUpIcon class="w-5 h-5" />
                </fwb-button>
            </div>
            <div class="mb-4" v-if="displayFileUploadBox == true">
                <fwb-file-input
                    v-model="userPhoto"
                    accept="image/jpeg,image/png,image/webp"
                    label="Upload Profile Picture (.jpeg / .jpg / .png / .webp)"
                    @change="handleFileChange"
                    dropzone
                />
            </div>
            <div class="mb-4 flex gap-2" v-if="displayFileUploadBox == true">
                <fwb-button
                    :disabled="canUploadPhoto == false"
                    @click="onClickUploadFile"
                    size="md"
                >
                    Upload
                </fwb-button>
                <fwb-button
                    @click="onClickDisplayFileUploadButton"
                    color="red"
                    size="md"
                >
                    Cancel
                </fwb-button>
            </div>
            <div class="mb-4" v-if="displayFileUploadSpinner == true">
                <label class="block mb-2 text-sm font-medium text-black-700">
                    Upload Profile Picture (.jpeg / .jpg / .png / .webp)
                </label>
                <fwb-spinner size="10" />
            </div>
            <div class="mb-4" v-if="displayFileUploadPhoto == true">
                <label class="block mb-2 text-sm font-medium text-black-700">
                    Upload Profile Picture (.jpeg / .jpg / .png / .webp)
                </label>
                <fwb-avatar
                    size="xl"
                    :img="`${BACKEND_URL}/${picture}`"
                />
            </div>
            <div class="mb-4 flex gap-2" v-if="displayFileUploadPhoto == true">
                <fwb-button
                    @click="onClickReuploadFile"
                    size="md"
                >
                    Re-upload
                </fwb-button>
                <fwb-button
                    @click="onClickCancelUploadedFile"
                    color="red"
                    size="md"
                >
                    Cancel
                </fwb-button>
            </div>
            <div class="flex gap-3">
                <fwb-button class="w-24" color="default" pill @click="cancelUpdate">Cancel</fwb-button>
                <fwb-button :disabled="!isUserTypeValid" class="disabled:opacity-50 w-24" color="default" pill type="submit">Save</fwb-button>
            </div>
        </form>
    </div>
</template>

<style scoped>

</style>