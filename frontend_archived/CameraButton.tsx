import * as React from 'react';
import {
  Text,
  TouchableOpacity,
  StyleSheet,
  GestureResponderEvent,
  OpaqueColorValue,
} from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import useColorScheme from '../../hooks/useColorScheme';
import Colors from '../../constants/Colors';

interface Props {
  title?: any,
  onPress?: ((event: GestureResponderEvent) => void) | undefined,
  icon?: any,
  color?: string | OpaqueColorValue | undefined,
  disabled?: boolean
}

export default function CameraButton({ title, onPress, icon, color, disabled }: Props) {
  const scheme = useColorScheme();

  return (
    <TouchableOpacity
      onPress={onPress}
      style={styles.button}
      disabled={disabled}
    >
      <FontAwesome name={icon} size={28} color={color ? color : '#f1f1f1'} />
      <Text style={[styles.text, { color: Colors[scheme].text }]}>{title}</Text>
    </TouchableOpacity>
  )
}

const styles = StyleSheet.create({
  button: {
    height: 40,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    fontWeight: 'bold',
    fontSize: 16,
    marginLeft: 10,
  },
})
