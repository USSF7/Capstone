<!-- Complete profile after registration/OAuth -->
<script lang="js" setup>

import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { FwbInput, FwbCheckbox, FwbA, FwbButton, FwbAvatar, FwbFileInput, FwbSpinner } from 'flowbite-vue'
import { DocumentArrowUpIcon } from '@heroicons/vue/24/solid'
import { useAuthStore } from '../../stores/auth'
import UserService from '../../services/userService'
import authService from '../../services/authService'

/**
 * Backend base URL for serving uploaded profile images.
 */
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL

/**
 * Maximum allowed profile picture size (2MB).
 */
const MAX_FILE_SIZE = 2 * 1024 * 1024

/**
 * Router instance for navigation.
 */
const router = useRouter()

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
 * Terms and condition state.
 */
const termsAndConditions = ref(false)

/**
 * User role vendor status.
 */
const vendorStatus = ref(false)

/**
 * User role renter status.
 */
const renterStatus = ref(false)

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
 * Ensures at least one user role is selected.
 */
const isUserTypeValid = computed(() => {
    return vendorStatus.value || renterStatus.value
})

/**
 * Ensures terms & conditions are accepted.
 */
const isTermsConditionsValid = computed(() => {
    return termsAndConditions.value
})

/**
 * Preload user info if authenticated.
 */
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
 * Submits completed profile data to the backend.
 */
async function submitProfile() {
    try {
        await UserService.updateUser(
            auth.user.id,
            firstName.value + " " + lastName.value,
            auth.user.email,
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
        alert(error.message || "Profile could not be saved. Please try again.")
    }
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
                <label class="block text-sm font-medium">Primary Site Usage</label>
                <p class="text-xs text-gray-500">
                    This setting just controls which navigation items are shown.
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
            <fwb-checkbox v-model="termsAndConditions">
                I agree with
                <fwb-a class="text-blue-600 hover:underline" href="#">
                    terms and conditions.
                </fwb-a>
            </fwb-checkbox>
            <fwb-button :disabled="!isUserTypeValid || !isTermsConditionsValid" class="disabled:opacity-50 w-full" color="default" type="submit">Complete Profile</fwb-button>
        </form>
    </div>
</template>
